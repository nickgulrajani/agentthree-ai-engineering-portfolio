.PHONY: setup verify demo help

setup:
	python3 -m venv .venv
	.venv/bin/pip install -q -e ".[dev]"

# Creates .venv if missing, then runs pytest + the CLI demo.
verify: setup
	.venv/bin/python -m pytest -q
	.venv/bin/python -m agentthree_aws_finops.cli demo
	@if command -v opa >/dev/null 2>&1; then opa test policy/; else echo "OPA not on PATH — skipping Rego suite (Python policy tests already ran)."; fi

demo: setup
	.venv/bin/agentthree-finops demo

serve: setup
	.venv/bin/agentthree-finops serve

help:
	@echo "make setup    # venv + install"
	@echo "make verify   # setup if needed, then pytest + demo"
	@echo "make demo     # CLI showcase"
	@echo "make serve    # HTML lab at http://127.0.0.1:8766/"
