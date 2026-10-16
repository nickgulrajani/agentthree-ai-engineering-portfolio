"""Run the MCP server on localhost and print ready-to-paste curl commands. Run: make serve"""

import shlex

import uvicorn

from . import ROOT
from .agents import Environment


def main(port: int = 8765):
    env = Environment(audit_path=ROOT / "artifacts" / "audit-live.jsonl")
    url = f"http://127.0.0.1:{port}/mcp"
    body = '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"query_records","arguments":{"dataset":"claims","purpose":"claims-adjudication"}}}'
    print("\nShort-lived tokens (TTL %ss) minted via workload identity → broker exchange:\n" % env.trust["token_ttl_seconds"])
    for name in ("claims-agent", "marketing-agent"):
        tok = env.agent(name).credential(env.resource, "records:read").access_token
        print(f"# {name} ({env.trust['workloads'][name]['cloud']})")
        print(f"curl -s {url} -H 'Authorization: Bearer {tok}' -H 'Content-Type: application/json' -d {shlex.quote(body)} | python3 -m json.tool\n")
    print(f"# no token → 401 + OAuth challenge\ncurl -si {url} -H 'Content-Type: application/json' -d {shlex.quote(body)}\n")
    print(f"Audit log (tail -f): {ROOT / 'artifacts' / 'audit-live.jsonl'}\n")
    uvicorn.run(env.app, host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()
