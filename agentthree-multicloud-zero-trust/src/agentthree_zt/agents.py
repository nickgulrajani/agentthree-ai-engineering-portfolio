"""Agents, agent-to-agent trust, and the assembled zero-trust environment."""

import itertools
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from .audit import AuditLog
from .clock import Clock
from .identity import CloudIssuer, Credential, Denied, TokenBroker, load_trust
from .mcp_server import create_app
from .policy import OPA


@dataclass
class CallResult:
    status: int
    allowed: bool
    records: list = field(default_factory=list)
    reasons: list = field(default_factory=list)


class Agent:
    def __init__(self, name: str, env: "Environment"):
        self.name = name
        self.env = env
        w = env.trust["workloads"].get(name)
        self.cloud = w["cloud"] if w else None
        self.subject = w["subject"] if w else None
        self._ids = itertools.count(1)

    def workload_token(self) -> str:
        """Projected service-account token from this agent's cloud OIDC issuer."""
        return self.env.issuers[self.cloud].projected_token(self.subject)

    def credential(self, audience: str, scope: str, actor_token: str | None = None) -> Credential:
        return self.env.broker.exchange(self.workload_token(), audience, scope, actor_token)

    def call_tool(self, token: str | None, tool: str, arguments: dict) -> CallResult:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        body = {"jsonrpc": "2.0", "id": next(self._ids), "method": "tools/call",
                "params": {"name": tool, "arguments": arguments}}
        r = self.env.http.post("/mcp", json=body, headers=headers)
        msg = r.json()
        if "error" in msg:
            data = msg["error"].get("data") or {}
            return CallResult(r.status_code, False, reasons=data.get("reasons") or [data.get("reason", msg["error"]["message"])])
        return CallResult(r.status_code, True, records=msg["result"]["structuredContent"]["records"])

    def query(self, dataset: str, purpose: str) -> CallResult:
        try:
            cred = self.credential(self.env.resource, "records:read")
        except Denied as d:
            return CallResult(0, False, reasons=[d.reason])
        return self.call_tool(cred.access_token, "query_records", {"dataset": dataset, "purpose": purpose})

    # --- agent-to-agent -------------------------------------------------
    def delegate(self, callee: "Agent", dataset: str, purpose: str) -> CallResult:
        """Ask another agent to perform a task, presenting an audience-bound A2A token."""
        try:
            a2a = self.credential(f"agent://{callee.name}", "a2a:delegate")
        except Denied as d:
            return CallResult(0, False, reasons=[d.reason])
        return callee.handle_task(a2a.access_token, {"dataset": dataset, "purpose": purpose})

    def handle_task(self, caller_token: str, task: dict, skip_a2a_check: bool = False) -> CallResult:
        env = self.env
        try:
            caller = env.broker.verify_access_token(caller_token, audience=f"agent://{self.name}")
        except Denied as d:
            env.audit.record("a2a", "accept_task", "unknown", "deny", callee=self.name, reason=d.reason)
            return CallResult(0, False, reasons=[d.reason])
        if not skip_a2a_check:
            decision = env.opa.decide("a2a", {"now": env.clock.now(), "callee": self.name, "caller": caller, "task": task})
            if not decision["allow"]:
                env.audit.record("a2a", "accept_task", caller["sub"], "deny", callee=self.name, task=task,
                                 reasons=sorted(decision["reasons"]))
                return CallResult(0, False, reasons=sorted(decision["reasons"]))
            env.audit.record("a2a", "accept_task", caller["sub"], "allow", callee=self.name, task=task)
        cred = self.credential(env.resource, "records:read", actor_token=caller_token)
        return self.call_tool(cred.access_token, "query_records", task)


class Environment:
    """Wires issuers, broker, OPA, MCP server, and audit log in-process (no ports, no cloud)."""

    def __init__(self, audit_path: Path | None = None, clock: Clock | None = None):
        self.trust = load_trust()
        self.clock = clock or Clock()
        self.audit = AuditLog(audit_path, self.clock)
        self.broker = TokenBroker(self.trust, self.audit, self.clock)
        self.issuers = {}
        for cloud, cfg in self.trust["issuers"].items():
            issuer = CloudIssuer(cloud, cfg["issuer"], cfg["audience"], self.clock)
            self.issuers[cloud] = issuer
            self.broker.register_issuer(issuer)
        self.opa = OPA()
        self.resource = self.trust["mcp_resource"]
        self.app = create_app(self.broker, self.opa, self.audit, self.resource)
        self.http = _SyncASGIClient(self.app)

    def agent(self, name: str) -> Agent:
        return Agent(name, self)

    def rogue_issuer(self, cloud: str = "aws") -> CloudIssuer:
        """Attacker-controlled issuer that copies a real issuer's URL but has its own key."""
        cfg = self.trust["issuers"][cloud]
        return CloudIssuer(cloud, cfg["issuer"], cfg["audience"], self.clock)


class _SyncASGIClient:
    """Synchronous facade over the ASGI app via fastapi's TestClient (real HTTP semantics, no socket)."""

    def __init__(self, app):
        from fastapi.testclient import TestClient
        self._c = TestClient(app, base_url="https://mcp.agentthree.local")

    def post(self, path, **kw) -> httpx.Response:
        return self._c.post(path, **kw)

    def get(self, path, **kw) -> httpx.Response:
        return self._c.get(path, **kw)

