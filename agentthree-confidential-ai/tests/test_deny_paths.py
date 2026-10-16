"""Deny-path proofs: wrong digest, debug TEE, expired attestation token."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from agentthree_confidential_ai.attestation.quote import issue_quote
from agentthree_confidential_ai.control_plane import ConfidentialControlPlane

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "configs" / "policy.yaml"
PHI = b"SYNTHETIC PHI: MRN-DENY-PATH | Dx: atrial fibrillation"
APPROVED_DIGEST = "sha256:demo-attested-vllm-0001"


@pytest.fixture()
def plane(tmp_path: Path) -> ConfidentialControlPlane:
    return ConfidentialControlPlane.from_paths(POLICY, tmp_path / "access.jsonl")


def test_wrong_image_digest_denied(plane: ConfidentialControlPlane) -> None:
    blob = plane.seal_sample(PHI, data_class="PHI")
    quote = issue_quote(
        workload_id="llm-inference-vllm",
        image_digest="sha256:wrong-or-tampered-image",
    )
    result = plane.request_decrypt(blob, quote=quote, purpose="inference")
    assert result.allowed is False
    assert result.plaintext is None
    assert "IMAGE_MISMATCH" in result.reason


def test_debug_mode_enabled_denied(plane: ConfidentialControlPlane) -> None:
    blob = plane.seal_sample(PHI, data_class="PHI")
    quote = issue_quote(
        workload_id="llm-inference-vllm",
        image_digest=APPROVED_DIGEST,
        debug_mode=True,
    )
    result = plane.request_decrypt(blob, quote=quote, purpose="inference")
    assert result.allowed is False
    assert result.plaintext is None
    assert result.attestation_ok is False
    assert "DEBUG" in result.reason or "DEBUG" in result.decision_details["attestation"]


def test_expired_attestation_token_denied(plane: ConfidentialControlPlane) -> None:
    blob = plane.seal_sample(PHI, data_class="PHI")
    quote = issue_quote(
        workload_id="llm-inference-vllm",
        image_digest=APPROVED_DIGEST,
        issued_at=int(time.time()) - 301,  # past default 300s max age
    )
    result = plane.request_decrypt(blob, quote=quote, purpose="inference")
    assert result.allowed is False
    assert result.plaintext is None
    assert result.attestation_ok is False
    assert "EXPIRED" in result.reason or "EXPIRED" in result.decision_details["attestation"]


def test_nonce_mismatch_denied(plane: ConfidentialControlPlane) -> None:
    blob = plane.seal_sample(PHI, data_class="PHI")
    quote = issue_quote(
        workload_id="llm-inference-vllm",
        image_digest=APPROVED_DIGEST,
        nonce="bound-to-session-aaa",
    )
    result = plane.request_decrypt(
        blob,
        quote=quote,
        purpose="inference",
        expected_nonce="bound-to-session-bbb",
    )
    assert result.allowed is False
    assert result.attestation_ok is False
    assert "NONCE" in result.decision_details["attestation"]
