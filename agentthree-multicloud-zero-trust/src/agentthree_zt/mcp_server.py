"""MCP records server (JSON-RPC 2.0 over Streamable HTTP) with OAuth bearer auth.

Follows the MCP authorization model: the server is an OAuth protected resource
(RFC 9728 metadata), rejects tokens not issued for its own resource URI, and
authorizes every tools/call through OPA before touching data.
"""

import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import RECORDS_PATH
from .audit import AuditLog
from .identity import Denied, TokenBroker
from .keys import decode_unverified
from .policy import OPA

PROTOCOL_VERSION = "2025-06-18"

TOOLS = [
    {
        "name": "list_datasets",
        "description": "List datasets this agent is entitled to query.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_records",
        "description": "Return records from a dataset, filtered to the caller's clearance.",
        "inputSchema": {
            "type": "object",
            "properties": {"dataset": {"type": "string"}, "purpose": {"type": "string"}},
            "required": ["dataset", "purpose"],
        },
    },
]


def _rpc_error(rpc_id, code: int, message: str, data: dict | None = None, status: int = 200, headers=None):
    body = {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": code, "message": message, **({"data": data} if data else {})}}
    return JSONResponse(body, status_code=status, headers=headers)


def _rpc_result(rpc_id, result: dict):
    return JSONResponse({"jsonrpc": "2.0", "id": rpc_id, "result": result})


def create_app(broker: TokenBroker, opa: OPA, audit: AuditLog, resource: str, records_path=RECORDS_PATH) -> FastAPI:
    app = FastAPI(title="AgentThree MCP Records Server")
    records = json.loads(records_path.read_text())
    metadata_url = "/.well-known/oauth-protected-resource"
    challenge = {"WWW-Authenticate": f'Bearer resource_metadata="{metadata_url}"'}

    @app.get(metadata_url)
    def protected_resource_metadata():
        return {
            "resource": resource,
            "authorization_servers": [broker.trust["broker_issuer"]],
            "scopes_supported": ["records:read"],
            "bearer_methods_supported": ["header"],
        }

    @app.post("/mcp")
    async def mcp(request: Request):
        msg = await request.json()
        rpc_id, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}

        auth = request.headers.get("authorization", "")
        if not auth.lower().startswith("bearer "):
            audit.record("mcp", method or "?", "anonymous", "deny", reason="missing bearer token")
            return _rpc_error(rpc_id, -32001, "Unauthorized", status=401, headers=challenge)
        try:
            claims = broker.verify_access_token(auth[7:], audience=resource)
        except Denied as d:
            try:
                claimed = f"{decode_unverified(auth[7:]).get('sub')} (unverified)"
            except Exception:
                claimed = "unknown"
            audit.record("mcp", method or "?", claimed, "deny", reason=d.reason)
            return _rpc_error(rpc_id, -32001, "Unauthorized", {"reason": d.reason}, status=401, headers=challenge)

        if method == "initialize":
            return _rpc_result(rpc_id, {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {"name": "agentthree-records", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            })
        if method == "tools/list":
            return _rpc_result(rpc_id, {"tools": TOOLS})
        if method != "tools/call":
            return _rpc_error(rpc_id, -32601, f"Method not found: {method}")

        tool, args = params.get("name"), params.get("arguments") or {}
        decision = opa.decide("mcp", {
            "resource": resource, "now": broker.clock.now(), "token": claims, "tool": tool, "args": args,
        })
        who = claims["sub"]
        extra = {"cloud": claims.get("cloud"), "jti": claims.get("jti")}
        if "delegation" in claims:
            extra["delegated_by"] = claims["delegation"]["from"]

        if not decision["allow"]:
            reasons = sorted(decision["reasons"])
            audit.record("mcp", f"tools/call:{tool}", who, "deny", args=args, reasons=reasons, **extra)
            return _rpc_error(rpc_id, -32003, "Forbidden by policy", {"reasons": reasons}, status=403)

        allowed = set(decision["permitted_classifications"])
        if tool == "list_datasets":
            payload = sorted({r["dataset"] for r in records})
            audit.record("mcp", f"tools/call:{tool}", who, "allow", **extra)
        else:
            in_ds = [r for r in records if r["dataset"] == args["dataset"]]
            payload = [r for r in in_ds if r["classification"] in allowed]
            withheld = [r["id"] for r in in_ds if r["classification"] not in allowed]
            audit.record("mcp", f"tools/call:{tool}", who, "allow", args=args,
                         returned=[r["id"] for r in payload], withheld=withheld, **extra)
        return _rpc_result(rpc_id, {
            "content": [{"type": "text", "text": json.dumps(payload)}],
            "structuredContent": {"records": payload},
            "isError": False,
        })

    return app
