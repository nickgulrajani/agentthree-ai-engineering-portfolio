"""End-to-end allow/deny integration tests: identity -> broker -> MCP -> OPA -> audit."""

from agentthree_zt.audit import load, verify_chain


def test_authorized_agent_gets_only_permitted_records(env):
    r = env.agent("claims-agent").query("claims", "claims-adjudication")
    assert r.allowed and r.status == 200
    ids = {rec["id"] for rec in r.records}
    assert ids == {"CLM-1001", "CLM-1002", "CLM-1003", "CLM-1005"}
    assert "CLM-1004" not in ids  # restricted record withheld
    assert {rec["store"].split(":")[0] for rec in r.records} == {"aws", "azure", "gcp"}

    entry = env.audit.entries[-1]
    assert entry["decision"] == "allow" and entry["withheld"] == ["CLM-1004"]


def test_unauthorized_agent_denied_and_audited(env):
    r = env.agent("marketing-agent").query("claims", "claims-adjudication")
    assert not r.allowed and r.status == 403
    assert 'dataset "claims" not entitled' in r.reasons
    assert r.records == []

    denial = env.audit.denials()[-1]
    assert denial["principal"] == "marketing-agent"
    assert denial["cloud"] == "gcp"
    assert denial["action"] == "tools/call:query_records"


def test_wrong_purpose_denied(env):
    r = env.agent("claims-agent").query("claims", "marketing")
    assert r.status == 403 and 'purpose "marketing" not entitled' in r.reasons


def test_unknown_workload_has_no_federated_credential(env):
    rogue = env.agent("claims-agent")
    rogue.subject = "system:serviceaccount:default:crypto-miner"
    r = rogue.query("claims", "claims-adjudication")
    assert not r.allowed and r.status == 0
    assert "no federated credential" in r.reasons[0]
    assert env.audit.denials()[-1]["component"] == "broker"


def test_forged_token_from_rogue_issuer_rejected(env):
    forged = env.rogue_issuer("aws").projected_token("system:serviceaccount:agents:claims-agent")
    try:
        env.broker.exchange(forged, env.resource, "records:read")
        raise AssertionError("forged token accepted")
    except Exception as e:
        assert "Signature verification failed" in str(e)
    assert env.audit.denials()[-1]["action"] == "token_exchange"


def test_scope_escalation_denied(env):
    agent = env.agent("orchestrator")
    try:
        agent.credential(env.resource, "records:read")
        raise AssertionError("escalation allowed")
    except Exception as e:
        assert "exceeds trust grant" in str(e)


def test_short_lived_token_expires(env):
    agent = env.agent("claims-agent")
    cred = agent.credential(env.resource, "records:read")
    assert cred.expires_in == 300
    args = {"dataset": "claims", "purpose": "claims-adjudication"}
    assert agent.call_tool(cred.access_token, "query_records", args).allowed
    env.clock.advance(301)
    r = agent.call_tool(cred.access_token, "query_records", args)
    assert r.status == 401 and r.reasons == ["access token expired"]


def test_token_for_other_audience_rejected_by_mcp(env):
    agent = env.agent("orchestrator")
    a2a = agent.credential("agent://claims-agent", "a2a:delegate")
    r = agent.call_tool(a2a.access_token, "query_records", {"dataset": "claims", "purpose": "claims-adjudication"})
    assert r.status == 401 and "Audience" in r.reasons[0]


def test_missing_token_gets_oauth_challenge(env):
    resp = env.http.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert resp.status_code == 401
    assert "resource_metadata" in resp.headers["www-authenticate"]
    meta = env.http.get("/.well-known/oauth-protected-resource").json()
    assert meta["resource"] == env.resource


def test_a2a_delegation_allowed(env):
    r = env.agent("orchestrator").delegate(env.agent("claims-agent"), "claims", "claims-adjudication")
    assert r.allowed and len(r.records) == 4
    last = env.audit.entries[-1]
    assert last["principal"] == "claims-agent" and last["delegated_by"] == "orchestrator"


def test_a2a_confused_deputy_denied(env):
    r = env.agent("marketing-agent").delegate(env.agent("claims-agent"), "claims", "claims-adjudication")
    assert not r.allowed
    assert '"marketing-agent" may not delegate to "claims-agent"' in r.reasons
    assert env.audit.denials()[-1]["component"] == "a2a"


def test_compromised_callee_still_blocked_at_mcp(env):
    """Even if claims-agent skips its A2A check, the MCP policy re-validates the delegation chain."""
    marketing, claims = env.agent("marketing-agent"), env.agent("claims-agent")
    a2a = marketing.credential("agent://claims-agent", "a2a:delegate")
    r = claims.handle_task(a2a.access_token, {"dataset": "claims", "purpose": "claims-adjudication"}, skip_a2a_check=True)
    assert r.status == 403
    assert '"marketing-agent" may not delegate to "claims-agent"' in r.reasons


def test_audit_log_is_tamper_evident(env, tmp_path):
    env.agent("claims-agent").query("claims", "claims-adjudication")
    env.agent("marketing-agent").query("claims", "claims-adjudication")
    entries = load(tmp_path / "audit.jsonl")
    assert verify_chain(entries) == (True, None)

    # Attacker tries to erase the denial.
    tampered = [dict(e) for e in entries]
    tampered[-1]["decision"] = "allow"
    ok, bad_seq = verify_chain(tampered)
    assert not ok and bad_seq == tampered[-1]["seq"]
