# How to run the Hands-On AI Architecture Lab

Everything is local. You will not be billed by AWS, Azure, GCP, or any model API.

## 1. Verify (required)

```bash
git clone https://github.com/nickgulrajani/agentthree-ai-architect-lab.git
cd agentthree-ai-architect-lab
make verify
```

`make verify` creates `.venv`, installs the package, runs pytest, and prints the CLI demo. No network calls.

Or from the [portfolio monorepo](https://github.com/nickgulrajani/agentthree-ai-engineering-portfolio):

```bash
cd agentthree-ai-architect-lab
make verify
```

## 2. Open the HTML lab (optional)

```bash
.venv/bin/agentthree-architect serve
```

Opens [http://127.0.0.1:8767/](http://127.0.0.1:8767/). Leave the badge on **SIMULATED · zero cost**. Do not paste an API key unless you intentionally want a live Anthropic call from the browser.

You can also open `web/index.html` directly in a browser.

## 3. Talk track

1. **Solution** — lending assistant: model writes, code decides.
2. **Agent graph** — run the $180k preset (prequalifies) then the injection preset (blocked).
3. **Router** — turn PII on; public Anthropic/OpenAI rows become ineligible.
4. **Evals** — run the suite; CI gate should allow merge.
