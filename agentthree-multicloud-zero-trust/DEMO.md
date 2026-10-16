# Presenter script (≈6 minutes)

**Setup (before the call):** `make setup && make verify`. Open the logo/storyboard in a browser tab and use a large terminal font.

1. **Frame it (30s).** Show the logo slide. "AI agents are workloads. Each one gets a cryptographic identity, a credential that expires within minutes, and a policy check on every tool call, on every cloud. Nothing here needs a cloud account."

2. **One source of truth (45s).** Open `config/trust.json`, then `infra/envs/demo/main.tf`. "Terraform provisions the IRSA role, the Entra federated credential and the GCP WIF pool from this file. The runtime enforces the same file."

3. **Run it (3 min).** `make demo-step`
   - Scenario 1: the authorized agent gets 4 records, and `CLM-1004` is withheld. *Least privilege applies even inside an allowed call.*
   - Scenario 2: the GCP marketing agent gets **403**, and the response says why.
   - Scenarios 3–5: cross-cloud A2A delegation works, and the laundering attempt is blocked twice (defense in depth).
   - Scenarios 6–7: a forged identity and an expired token are both rejected.
   - Audit table: every decision is logged, and the tamper test flags the edited entry.

4. **Evidence (45s).** Open `artifacts/evidence-report.html`. "This is what an auditor or an insurer gets: what was allowed, what was denied and why, with tamper-evident records."

5. **Prove it's real (optional, 1 min).** `make serve`, then paste the two printed curl commands: 200 vs 403 over real HTTP.

6. **Close (15s).** `make verify`: Rego, integration and Terraform tests are all green, with $0 cloud spend.

**Likely questions**
- *"Is this just a mock?"* Only the cloud control planes are local stand-ins. The JWT signing and verification, the token exchange, the OPA decisions, the MCP OAuth flow and the audit chain all run for real, and the Terraform is valid and tested.
- *"How does this go to production?"* Replace the local issuers with the real EKS, AKS and GKE OIDC issuers, and the broker with STS, Entra and GCP STS. Run OPA as a sidecar and send the audit log to CloudTrail, Sentinel or Chronicle.
