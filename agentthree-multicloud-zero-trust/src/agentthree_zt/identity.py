"""Workload identity issuers and the STS-style token broker.

Each cloud's OIDC issuer (EKS / AKS / GKE) mints a projected service-account
token. The broker plays the role of AWS STS AssumeRoleWithWebIdentity, Entra
workload identity federation, and GCP STS: it verifies the token against the
trust configuration in config/trust.json (the same file Terraform consumes)
and returns a short-lived, audience-bound access token.
"""

import json
import uuid
from dataclasses import dataclass

import jwt

from . import CONFIG_PATH
from .audit import AuditLog
from .clock import Clock
from .keys import Signer, decode_unverified, verify


class Denied(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def load_trust(path=CONFIG_PATH) -> dict:
    return json.loads(path.read_text())


class CloudIssuer(Signer):
    """Simulated EKS/AKS/GKE OIDC issuer for projected service-account tokens."""

    def __init__(self, cloud: str, issuer: str, audience: str, clock: Clock):
        super().__init__(issuer)
        self.cloud = cloud
        self.audience = audience
        self.clock = clock

    def projected_token(self, subject: str, ttl: int = 600) -> str:
        now = self.clock.now()
        return self.sign({"sub": subject, "aud": self.audience, "iat": now, "exp": now + ttl})


@dataclass
class Credential:
    access_token: str
    expires_in: int
    scope: str
    cloud: str
    workload: str


class TokenBroker:
    def __init__(self, trust: dict, audit: AuditLog, clock: Clock):
        self.trust = trust
        self.audit = audit
        self.clock = clock
        self.signer = Signer(trust["broker_issuer"])
        self.issuers: dict[str, CloudIssuer] = {}
        self.by_subject = {(w["cloud"], w["subject"]): name for name, w in trust["workloads"].items()}

    def register_issuer(self, issuer: CloudIssuer) -> None:
        self.issuers[issuer.issuer] = issuer

    @property
    def public_key(self):
        return self.signer.public_key

    def _verify_workload(self, subject_token: str) -> tuple[str, dict]:
        try:
            unverified = decode_unverified(subject_token)
        except jwt.PyJWTError as e:
            raise Denied(f"malformed subject token: {e}")
        issuer = self.issuers.get(unverified.get("iss"))
        if issuer is None:
            raise Denied(f"untrusted issuer {unverified.get('iss')!r}")
        expected = self.trust["issuers"][issuer.cloud]
        try:
            claims = verify(subject_token, issuer.public_key, audience=expected["audience"])
        except jwt.PyJWTError as e:
            raise Denied(f"subject token rejected: {e}")
        if self.clock.now() >= claims["exp"]:
            raise Denied("subject token expired")
        name = self.by_subject.get((issuer.cloud, claims["sub"]))
        if name is None:
            raise Denied(f"no federated credential for {issuer.cloud}:{claims['sub']}")
        return name, claims

    def exchange(self, subject_token: str, audience: str, scope: str,
                 actor_token: str | None = None) -> Credential:
        """RFC 8693-style token exchange. Optional actor_token records A2A delegation."""
        principal = decode_unverified(subject_token).get("sub", "?") if subject_token.count(".") == 2 else "?"
        try:
            name, _ = self._verify_workload(subject_token)
            principal = name
            workload = self.trust["workloads"][name]
            requested = set(scope.split())
            if not requested <= set(workload["scopes"]):
                raise Denied(f"scope {sorted(requested - set(workload['scopes']))} exceeds trust grant")
            delegation = None
            if actor_token:
                actor = self.verify_access_token(actor_token, audience=f"agent://{name}")
                prior = actor.get("delegation", {}).get("chain", [])
                delegation = {"from": actor["sub"], "chain": [*prior, actor["sub"]]}
        except Denied as d:
            self.audit.record("broker", "token_exchange", principal, "deny", reason=d.reason, audience=audience)
            raise

        now = self.clock.now()
        ttl = self.trust["token_ttl_seconds"]
        claims = {"sub": name, "aud": audience, "iat": now, "exp": now + ttl,
                  "jti": uuid.uuid4().hex, "scope": scope, "cloud": workload["cloud"]}
        if delegation:
            claims["delegation"] = delegation
        token = self.signer.sign(claims)
        self.audit.record("broker", "token_exchange", name, "allow", cloud=workload["cloud"],
                          audience=audience, scope=scope, ttl=ttl, jti=claims["jti"],
                          **({"delegated_by": delegation["from"]} if delegation else {}))
        return Credential(token, ttl, scope, workload["cloud"], name)

    def verify_access_token(self, token: str, audience: str) -> dict:
        try:
            claims = verify(token, self.public_key, audience=audience)
        except jwt.PyJWTError as e:
            raise Denied(f"access token rejected: {e}")
        if self.clock.now() >= claims["exp"]:
            raise Denied("access token expired")
        return claims
