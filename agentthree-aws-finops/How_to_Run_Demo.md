# How to run the AWS FinOps demo

Local only. **No AWS account, no boto3, no Cost Explorer, no cloud spend.**

You need Python 3.10+ on your machine. You do **not** need AWS credentials.

---

## 1. Open the project

From the portfolio monorepo:

```bash
cd agentthree-aws-finops
```

Or clone the standalone repo:

```bash
git clone https://github.com/nickgulrajani/agentthree-aws-finops.git
cd agentthree-aws-finops
```

## 2. One-command verify (venv + tests + CLI)

```bash
make verify
```

That creates `.venv` if it is missing, installs the package, runs **8 pytest cases**, then `agentthree-finops demo`. Optional: `opa test policy/` if [OPA](https://www.openpolicyagent.org/docs/latest/#running-opa) is installed.

Expected: `8 passed`, then the See → Allocate → Guard → Optimize tables.

## 3. CLI demo only

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
agentthree-finops demo
```

What you should see:

| Step | Result |
|------|--------|
| 01 See | $412.8k/mo · 61% tagged · $2.58 per 1k card transactions |
| 02 Allocate | tag standard applied locally → **91%** coverage |
| 03–04 Guard | `deny_untagged.json` **FAIL** · `allow_tagged.json` **PASS** · Infracost fixture **WARN** |
| 05 Optimize | all recs selected → **$324.8k** run rate · **$2.03** unit cost |

Those numbers are fixtures in `configs/` and `data/`. Nothing is read from AWS.

## 4. Browser storyboard

Keep the venv active:

```bash
agentthree-finops serve
```

Opens http://127.0.0.1:8766/ — the original HTML lab (Why → See → Allocate → Guard → Enforce → Optimize). Static files only. Google Fonts may load in the browser; that is not AWS.

Or open `web/index.html` directly.

## 5. Extra commands (still local)

```bash
agentthree-finops coverage --tag-all
agentthree-finops policy --plan data/plans/deny_untagged.json
agentthree-finops optimize --select all
pytest -q
```

---

## What this demo never does

- Call Cost Explorer, CUR, Athena, CloudWatch, or any other AWS API
- Use boto3 / AWS CLI
- Run `terraform apply` or change cloud resources
- Purchase Savings Plans or Reserved Instances

If a screen mentions those products, it is documenting what a real issuer would wire up later. Mapping: [docs/architecture.md](docs/architecture.md).
