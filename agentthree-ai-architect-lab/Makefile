.PHONY: setup verify demo help

setup:
	python3 -m venv .venv
	.venv/bin/pip install -q -e ".[dev]"

verify: setup
	.venv/bin/python -m pytest -q
	.venv/bin/python -m agentthree_ai_architect.cli demo

demo: setup
	.venv/bin/agentthree-architect demo

help:
	@echo "make setup   # venv + install"
	@echo "make verify  # pytest + CLI demo"
	@echo "make demo    # CLI showcase"
