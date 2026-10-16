"""In-memory RSA signers that stand in for cloud OIDC issuers and the STS broker."""

import json
import uuid

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm


class Signer:
    def __init__(self, issuer: str):
        self.issuer = issuer
        self.kid = uuid.uuid4().hex[:12]
        self._private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self.public_key = self._private.public_key()

    def sign(self, claims: dict) -> str:
        return jwt.encode({"iss": self.issuer, **claims}, self._private, algorithm="RS256", headers={"kid": self.kid})

    def jwks(self) -> dict:
        jwk = json.loads(RSAAlgorithm.to_jwk(self.public_key))
        return {"keys": [{**jwk, "kid": self.kid, "use": "sig", "alg": "RS256"}]}


def decode_unverified(token: str) -> dict:
    return jwt.decode(token, options={"verify_signature": False})


def verify(token: str, public_key, audience: str | None = None) -> dict:
    """Verify signature/audience. Expiry is checked by callers against the injectable clock."""
    return jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=audience,
        options={"verify_exp": False, "verify_aud": audience is not None},
    )
