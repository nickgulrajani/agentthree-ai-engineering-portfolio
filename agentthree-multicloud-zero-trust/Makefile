.PHONY: setup test policy-test tf-validate tf-test verify demo demo-step serve clean

PY        ?= .venv/bin/python
TERRAFORM ?= terraform
TF_DIR     = infra/envs/demo

setup:
	python3 -m venv .venv
	.venv/bin/pip install -q -r requirements.txt
	.venv/bin/pip install -q -e .
	@command -v opa >/dev/null || (echo "Install OPA: brew install opa" && exit 1)

policy-test:
	opa fmt --list --fail policy/ && opa test policy/ -v

test:
	$(PY) -m pytest -q

tf-validate:
	cd $(TF_DIR) && $(TERRAFORM) fmt -check -recursive ../../ && $(TERRAFORM) init -backend=false -input=false >/dev/null && $(TERRAFORM) validate

# Mock providers need Terraform >= 1.7 (brew install hashicorp/tap/terraform)
tf-test: tf-validate
	cd $(TF_DIR) && $(TERRAFORM) test

verify: policy-test test tf-test
	@echo "\n✔ policy, integration, and IaC tests passed — \$$0 cloud spend"

demo:
	$(PY) -m agentthree_zt.demo

demo-step:
	$(PY) -m agentthree_zt.demo --step

serve:
	$(PY) -u -m agentthree_zt.serve

clean:
	rm -rf .venv artifacts .pytest_cache
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
	find infra -name .terraform -type d -exec rm -rf {} + 2>/dev/null || true
