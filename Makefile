.PHONY: verify test help

# One command for reviewers: run every project's reproducible tests.
verify test:
	@chmod +x scripts/verify-all.sh
	@./scripts/verify-all.sh

help:
	@echo "make verify   # run pytest (and prior-auth eval) across all five projects"
	@echo "              # Zero Trust skips cleanly if OPA is not installed"
