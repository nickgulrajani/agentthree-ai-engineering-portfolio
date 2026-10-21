.PHONY: setup verify demo help

setup:
	python3 -m venv .venv
	.venv/bin/pip install -q -e ".[dev]"

verify:
	.venv/bin/python -m pytest -q
	.venv/bin/python -m agentthree_aws_finops.cli demo
	@if command -v opa >/dev/null 2>&1; then opa test policy/; else echo "OPA not on PATH — skipping Rego suite (Python policy tests already ran)."; fi

demo:
	.venv/bin/agentthree-finops demo

help:
	@echo "make setup    # venv + install"
	@echo "make verify   # pytest + demo (+ opa test if installed)"
	@echo "make demo     # CLI showcase"
