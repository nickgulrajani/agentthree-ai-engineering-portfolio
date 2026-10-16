# Demo image only — never pushed to a registry in the zero-billing pipeline.
# Trivy scans this file/directory locally; no cloud billing.
FROM python:3.12-slim

LABEL org.opencontainers.image.title="agentthree-ai-devsecops"
LABEL org.opencontainers.image.description="DevSecOps gate runner (local/CI dry-run)"
LABEL demo.purpose="container-scan-target"

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
COPY evaluation/ ./evaluation/
COPY scripts/ ./scripts/

CMD ["python", "-m", "agentthree_devsecops.evaluation", "--fixture", "evaluation/fixtures/pass_grounding.json"]
