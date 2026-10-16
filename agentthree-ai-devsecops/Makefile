.PHONY: setup test gates pass fail-checkov fail-eval fail-health demo clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .

test:
	.venv/bin/pytest -q

gates pass:
	./scripts/run-gates.sh pass

fail-checkov:
	./scripts/run-gates.sh fail-checkov || true

fail-eval:
	./scripts/run-gates.sh fail-eval || true

fail-health:
	./scripts/run-gates.sh fail-health || true

demo: pass
	@echo ""
	@echo "Now demonstrate blockers:"
	@echo "  make fail-checkov   # insecure Terraform blocked"
	@echo "  make fail-eval      # grounding score blocks promotion"
	@echo "  make fail-health    # canary failure → rollback dry-run"

clean:
	rm -rf .venv artifacts evaluation/last_results.json .pytest_cache
	find infra -name .terraform -type d -exec rm -rf {} + 2>/dev/null || true
