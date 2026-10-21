from __future__ import annotations

import http.server
import os
import socketserver
import webbrowser
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from agentthree_ai_architect.agent import run_agent
from agentthree_ai_architect.evals import PRESETS, run_eval_suite
from agentthree_ai_architect.router import RouteRequest, route

console = Console()
WEB = Path(__file__).resolve().parents[2] / "web"


@click.group()
def main() -> None:
    """Hands-On AI Architecture Lab — local, simulated, $0 cloud."""


@main.command()
def demo() -> None:
    """Print the simulated agent + eval gate (no network)."""
    console.print("[bold cyan]AgentThree · Hands-On AI Architecture Lab[/bold cyan]")
    console.print("Mode: [yellow]SIMULATED · zero cost[/yellow] — no cloud APIs\n")

    samples = [
        ("Strong applicant", PRESETS[1]),
        ("Injection", PRESETS[4]),
        ("PII + HITL", PRESETS[2]),
        ("Weak DSCR", PRESETS[3]),
    ]
    table = Table(title="Agent graph (deterministic)")
    table.add_column("Case")
    table.add_column("Outcome")
    table.add_column("Notes")
    for name, prompt in samples:
        s = run_agent(prompt)
        if s["blocked"]:
            outcome, notes = "blocked", "prompt injection"
        elif s["tool"]:
            outcome = s["tool"]["decision"]
            notes = "HITL" if s["needs_human"] else f"PII redacted={s['pii_found']}"
        else:
            outcome, notes = "answered", ",".join(s["citations"])
        table.add_row(name, outcome, notes)
    console.print(table)

    picked = route(
        RouteRequest(
            prompt="Prequalify with PII present",
            tin=800,
            tout=400,
            pii=True,
        )
    )
    pick = picked["pick"]
    console.print(
        f"\nRouter (PII on): [green]{pick['name']}[/green] via {pick['via']}  (private endpoint)"
    )

    suite = run_eval_suite()
    color = "green" if suite["gate"] == "MERGE ALLOWED" else "red"
    console.print(
        f"Eval gate: [{color}]{suite['passed']}/{suite['total']} passed · {suite['gate']}[/{color}]"
    )


@main.command()
@click.option("--port", default=8767, show_default=True)
@click.option("--no-browser", is_flag=True)
def serve(port: int, no_browser: bool) -> None:
    """Serve web/index.html locally. Still simulated unless you paste a key in the page."""
    os.chdir(WEB)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/"
        console.print(f"Lab at {url}  (Ctrl+C to stop)")
        if not no_browser:
            webbrowser.open(url)
        httpd.serve_forever()
