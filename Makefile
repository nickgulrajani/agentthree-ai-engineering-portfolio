.PHONY: verify test help

# One command for reviewers: run every project's reproducible tests.
verify test:
	@chmod +x scripts/verify-all.sh
	@./scripts/verify-all.sh

help:
	@echo "make verify   # run pytest (and evals) across all eight projects"
	@echo "              # Zero Trust / FinOps skip Rego cleanly if OPA is not installed"
