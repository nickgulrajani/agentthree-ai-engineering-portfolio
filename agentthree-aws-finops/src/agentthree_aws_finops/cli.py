"""CLI: local FinOps demo for an illustrative card issuer — zero AWS cost."""

from __future__ import annotations

import http.server
import json
import socketserver
import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentthree_aws_finops.engine import load_state
from agentthree_aws_finops.optimize import (
    apply_selection,
    load_recommendations,
    monthly_savings_k,
    projected_run_rate_k,
    unit_cost_after,
)
from agentthree_aws_finops.policy import gate, load_json

console = Console()
ROOT = Path(__file__).resolve().parents[2]


@click.group()
@click.version_option(package_name="agentthree-aws-finops")
def main() -> None:
    """AgentThree AWS FinOps — simulated CUR, tags, policy gates, savings."""


@main.command("demo")
def demo() -> None:
    """Run the showcase: see spend, allocate tags, fail a bad plan, project savings."""
    console.print(
        Panel.fit(
            "[bold]AgentThree AWS FinOps Lab[/bold]\n"
            "Illustrative credit card issuer · local simulation\n"
            "[dim]No AWS account · no CUR · no Cost Explorer · $0 cloud spend[/dim]",
            border_style="cyan",
        )
    )

    state = load_state()
    before = Table(title="01 · See  (Oct 2026 fixture CUR)")
    before.add_column("KPI")
    before.add_column("Value", justify="right")
    before.add_row("Monthly spend", f"${state.monthly_spend_k:.1f}k")
    before.add_row("Tag coverage", f"{state.coverage:.0%}")
    before.add_row("Unallocated", f"${state.unallocated_k:.1f}k")
    before.add_row("Unit cost / 1k txns", f"${state.unit_cost_per_1k:.2f}")
    console.print(before)

    state.apply_tags()
    after = Table(title="02 · Allocate  (tag standard applied locally)")
    after.add_column("Team")
    after.add_column("Showback", justify="right")
    for team, amount in state.showback().items():
        after.add_row(team, f"${amount:.1f}k")
    after.add_row("Coverage", f"{state.coverage:.0%}  (target {state.coverage_target:.0%})")
    console.print(after)

    deny_plan = load_json(ROOT / "data" / "plans" / "deny_untagged.json")
    allow_plan = load_json(ROOT / "data" / "plans" / "allow_tagged.json")
    infracost = load_json(ROOT / "data" / "plans" / "infracost_warn.json")
    deny_status, deny_findings = gate(deny_plan)
    allow_status, _ = gate(allow_plan)
    warn_status, warn_findings = gate(allow_plan, infracost)

    gates = Table(title="03–04 · Guard / Enforce  (fixture Terraform plans)")
    gates.add_column("Plan")
    gates.add_column("Result")
    gates.add_column("Detail")
    gates.add_row(
        "deny_untagged.json",
        f"[red]{deny_status}[/red]",
        deny_findings[0].message if deny_findings else "",
    )
    gates.add_row("allow_tagged.json", f"[green]{allow_status}[/green]", "required tags present")
    gates.add_row(
        "infracost_warn.json",
        f"[yellow]{warn_status}[/yellow]",
        warn_findings[-1].message if warn_findings else "",
    )
    console.print(gates)

    recs = apply_selection(load_recommendations(), ["all"])
    save = monthly_savings_k(recs)
    run = projected_run_rate_k(state.monthly_spend_k, recs)
    unit = unit_cost_after(state.monthly_spend_k, state.transactions, recs)
    opt = Table(title="05 · Optimize  (all recs selected — math only)")
    opt.add_column("Measure")
    opt.add_column("Today", justify="right")
    opt.add_column("After", justify="right")
    opt.add_row("Monthly run rate", f"${state.monthly_spend_k:.1f}k", f"${run:.1f}k")
    opt.add_row("Monthly savings", "—", f"${save:.1f}k")
    opt.add_row("Unit cost / 1k txns", f"${state.unit_cost_per_1k:.2f}", f"${unit:.2f}")
    console.print(opt)

    if deny_status != "FAIL" or allow_status != "PASS" or state.coverage < state.coverage_target:
        raise SystemExit(1)
    console.print(
        "\n[bold]Demo complete:[/bold] coverage crossed 90%, untagged plan blocked, "
        "tagged plan passed. Open [cyan]web/index.html[/cyan] or run [cyan]agentthree-finops serve[/cyan]."
    )


@main.command("coverage")
@click.option("--tag-all", is_flag=True, help="Apply the tag standard to every untagged resource.")
def coverage(tag_all: bool) -> None:
    """Print tag coverage and showback from fixture CUR data."""
    state = load_state()
    if tag_all:
        state.apply_tags()
    console.print_json(
        json.dumps(
            {
                "coverage": round(state.coverage, 4),
                "allocated_k": round(state.allocated_k, 1),
                "unallocated_k": round(state.unallocated_k, 1),
                "unit_cost_per_1k": round(state.unit_cost_per_1k, 2),
                "showback_k": {k: round(v, 1) for k, v in state.showback().items()},
            }
        )
    )


@main.command("policy")
@click.option(
    "--plan",
    type=click.Path(path_type=Path, exists=True),
    default=ROOT / "data" / "plans" / "deny_untagged.json",
)
@click.option("--infracost", type=click.Path(path_type=Path, exists=True), default=None)
def policy_cmd(plan: Path, infracost: Path | None) -> None:
    """Evaluate a fixture Terraform plan (Python equivalent of the Rego policies)."""
    status, findings = gate(load_json(plan), load_json(infracost) if infracost else None)
    for finding in findings:
        color = {"deny": "red", "warn": "yellow"}.get(finding.severity, "white")
        console.print(f"[{color}]{finding.severity.upper()}[/{color}] {finding.rule} · {finding.message}")
    console.print(f"\n[bold]{status}[/bold]")
    raise SystemExit(0 if status != "FAIL" else 1)


@main.command("optimize")
@click.option("--select", default="defaults", help="defaults | all | comma-separated rec ids")
def optimize_cmd(select: str) -> None:
    """Project monthly savings from the architecture backlog (no AWS changes)."""
    recs = load_recommendations()
    if select == "all":
        apply_selection(recs, ["all"])
    elif select != "defaults":
        apply_selection(recs, [s.strip() for s in select.split(",") if s.strip()])
    state = load_state()
    save = monthly_savings_k(recs)
    console.print_json(
        json.dumps(
            {
                "selected": [r.id for r in recs if r.selected],
                "monthly_savings_k": round(save, 1),
                "projected_run_rate_k": projected_run_rate_k(state.monthly_spend_k, recs),
                "unit_cost_per_1k": round(
                    unit_cost_after(state.monthly_spend_k, state.transactions, recs), 2
                ),
            }
        )
    )


@main.command("serve")
@click.option("--port", default=8766, show_default=True)
@click.option("--open/--no-open", "open_browser", default=True)
def serve(port: int, open_browser: bool) -> None:
    """Serve the HTML lab locally (static files only — still no AWS)."""
    web = ROOT / "web"
    handler = http.server.SimpleHTTPRequestHandler

    class DirectoryHandler(handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(web), **kwargs)

    url = f"http://127.0.0.1:{port}/"
    console.print(f"Serving [cyan]{web}[/cyan] at {url}  (Ctrl+C to stop)")
    if open_browser:
        webbrowser.open(url)
    with socketserver.TCPServer(("127.0.0.1", port), DirectoryHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
