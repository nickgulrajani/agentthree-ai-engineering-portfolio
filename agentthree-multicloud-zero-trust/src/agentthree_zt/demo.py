"""Narrated zero-billing demo. Run: make demo"""

import argparse
import base64
import html
import json
import time

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import ROOT
from .agents import CallResult, Environment
from .audit import load, verify_chain

console = Console()
ARTIFACTS = ROOT / "artifacts"


def show(title: str, r: CallResult, expect_allow: bool) -> dict:
    ok = r.allowed == expect_allow
    verdict = "[bold green]ALLOW[/]" if r.allowed else "[bold red]DENY[/]"
    lines = [f"{verdict}  (HTTP {r.status or 'n/a — stopped at broker/A2A'})"]
    if r.records:
        lines += [f"  • {x['id']} [{x['classification']}] {x['store']}" for x in r.records]
    if r.reasons:
        lines += [f"  ✗ {x}" for x in r.reasons]
    lines.append("[green]✔ expected[/]" if ok else "[red]✘ UNEXPECTED[/]")
    console.print(Panel("\n".join(lines), title=title, border_style="green" if r.allowed else "red"))
    return {"title": title, "allowed": r.allowed, "expected": ok, "status": r.status,
            "records": [x["id"] for x in r.records], "reasons": r.reasons}


def pause(step: bool):
    if step:
        console.input("[dim]↵ next scenario[/]")


def run(step: bool = False) -> int:
    ARTIFACTS.mkdir(exist_ok=True)
    audit_path = ARTIFACTS / "audit.jsonl"
    env = Environment(audit_path=audit_path)
    claims, orch, mkt = env.agent("claims-agent"), env.agent("orchestrator"), env.agent("marketing-agent")

    console.rule("[bold cyan]AgentThree · Multi-Cloud Zero Trust for AI Agents")
    console.print("AWS (EKS IRSA) · Azure (AKS Workload ID) · GCP (GKE WIF) → token broker → MCP → OPA → audit\n"
                  "[dim]Local, in-process. No cloud accounts, no API keys, $0.[/]\n")
    results = []

    results.append(show("1 · Authorized agent (AWS claims-agent) retrieves permitted records",
                        claims.query("claims", "claims-adjudication"), True))
    console.print("[dim]   CLM-1004 is 'restricted' → withheld by row-level policy even though the agent is authorized.[/]")
    pause(step)
    results.append(show("2 · Unauthorized agent (GCP marketing-agent) requests claims → denied + audited",
                        mkt.query("claims", "claims-adjudication"), False))
    pause(step)
    results.append(show("3 · A2A: Azure orchestrator delegates to AWS claims-agent (cross-cloud)",
                        orch.delegate(claims, "claims", "claims-adjudication"), True))
    pause(step)
    results.append(show("4 · A2A confused deputy: marketing-agent tries to launder access via claims-agent",
                        mkt.delegate(claims, "claims", "claims-adjudication"), False))
    pause(step)
    a2a = mkt.credential("agent://claims-agent", "a2a:delegate")
    results.append(show("5 · Compromised callee skips its A2A check → MCP policy still blocks",
                        claims.handle_task(a2a.access_token, {"dataset": "claims", "purpose": "claims-adjudication"},
                                           skip_a2a_check=True), False))
    pause(step)
    forged = env.rogue_issuer("aws").projected_token(claims.subject)
    try:
        env.broker.exchange(forged, env.resource, "records:read")
        r5 = CallResult(200, True)
    except Exception as e:
        r5 = CallResult(0, False, reasons=[getattr(e, "reason", str(e))])
    results.append(show("6 · Forged workload token (attacker-run OIDC issuer) → rejected at broker", r5, False))
    pause(step)
    cred = claims.credential(env.resource, "records:read")
    env.clock.advance(cred.expires_in + 1)
    results.append(show(f"7 · Short-lived credential replayed after {cred.expires_in}s TTL → rejected",
                        claims.call_tool(cred.access_token, "query_records",
                                         {"dataset": "claims", "purpose": "claims-adjudication"}), False))

    entries = load(audit_path)
    ok, _ = verify_chain(entries)
    tampered = [dict(e) for e in entries]
    first_deny = next(e for e in tampered if e["decision"] == "deny")
    first_deny["decision"] = "allow"
    t_ok, t_seq = verify_chain(tampered)

    table = Table(title="Audit trail (hash-chained)", show_lines=False)
    for col in ("seq", "component", "action", "principal", "decision", "detail"):
        table.add_column(col)
    for e in entries:
        detail = e.get("reason") or "; ".join(e.get("reasons", [])) or (
            f"returned={e['returned']} withheld={e['withheld']}" if "returned" in e else e.get("scope", ""))
        if e.get("delegated_by"):
            detail = f"via {e['delegated_by']} · {detail}"
        color = "green" if e["decision"] == "allow" else "red"
        table.add_row(str(e["seq"]), e["component"], e["action"], e["principal"], f"[{color}]{e['decision']}[/]", detail)
    console.print(table)
    console.print(f"Chain integrity: {'[green]VALID[/]' if ok else '[red]BROKEN[/]'} ({len(entries)} entries) · "
                  f"tamper test (flip a deny→allow): {'[red]undetected[/]' if t_ok else f'[green]detected at seq {t_seq}[/]'}")

    report = write_report(results, entries, ok, t_seq)
    passed = all(r["expected"] for r in results) and ok and not t_ok
    console.rule("[bold green]ALL SCENARIOS AS EXPECTED" if passed else "[bold red]UNEXPECTED RESULT")
    console.print(f"Audit log: {audit_path}\nEvidence report: {report}")
    return 0 if passed else 1


def write_report(results, entries, chain_ok, tamper_seq):
    logo = base64.b64encode((ROOT / "docs/assets/logo.png").read_bytes()).decode()
    e = html.escape
    rows = "".join(
        f"<tr><td>{e(r['title'])}</td><td class={'allow' if r['allowed'] else 'deny'}>{'ALLOW' if r['allowed'] else 'DENY'}</td>"
        f"<td>{e(', '.join(r['records']) or '; '.join(r['reasons']))}</td><td>{'✔' if r['expected'] else '✘'}</td></tr>"
        for r in results)
    audit_rows = "".join(
        f"<tr><td>{x['seq']}</td><td>{e(x['component'])}</td><td>{e(x['action'])}</td><td>{e(x['principal'])}</td>"
        f"<td class={x['decision']}>{x['decision']}</td><td><code>{x['hash'][:16]}…</code></td></tr>" for x in entries)
    page = f"""<!doctype html><html><head><meta charset=utf-8><title>AgentThree Zero Trust Evidence</title>
<style>
body{{font:14px system-ui;background:#0b1530;color:#e6ecff;margin:0;padding:24px 16px}}
main{{max-width:1000px;margin:auto}} h1{{font-size:24px;margin:.2em 0}} h2{{font-size:16px;color:#8fb4ff;margin-top:28px}}
header{{display:flex;gap:20px;align-items:center;flex-wrap:wrap}} header img{{width:180px;border-radius:14px}}
.wrap{{overflow-x:auto}} table{{border-collapse:collapse;width:100%}} td,th{{border-bottom:1px solid #22325c;padding:6px 8px;text-align:left;vertical-align:top}}
.allow{{color:#4ade80;font-weight:600}} .deny{{color:#f87171;font-weight:600}} code{{color:#93c5fd}}
.pill{{display:inline-block;background:#13234a;border:1px solid #2b3f75;border-radius:999px;padding:3px 10px;margin:2px}}
</style></head><body><main>
<header><img src="data:image/png;base64,{logo}" alt="AgentThree multi-cloud zero trust">
<div><h1>Multi-Cloud Zero Trust for AI Agents</h1>
<div>Generated {time.strftime('%Y-%m-%d %H:%M:%S')} · local run · $0 cloud spend</div>
<div style="margin-top:8px"><span class=pill>Faster breach detection</span><span class=pill>Audit-ready architecture</span><span class=pill>Lower cyber-insurance premiums</span></div></div></header>
<h2>Scenarios</h2><div class=wrap><table><tr><th>Scenario</th><th>Decision</th><th>Records / reasons</th><th>Expected</th></tr>{rows}</table></div>
<h2>Audit chain — {'VALID' if chain_ok else 'BROKEN'} · tamper detected at seq {tamper_seq}</h2>
<div class=wrap><table><tr><th>#</th><th>Component</th><th>Action</th><th>Principal</th><th>Decision</th><th>Hash</th></tr>{audit_rows}</table></div>
<h2>Raw audit (JSONL)</h2><div class=wrap><pre>{e(chr(10).join(json.dumps(x) for x in entries))}</pre></div>
</main></body></html>"""
    path = ARTIFACTS / "evidence-report.html"
    path.write_text(page)
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--step", action="store_true", help="pause between scenarios (live presenting)")
    raise SystemExit(run(step=ap.parse_args().step))


if __name__ == "__main__":
    main()
