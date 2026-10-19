
“The model is a configuration choice, not an architectural one. I run Flash on the free tier for the demo. In production I’d move to Gemini on Vertex AI under the BAA, and before switching models I’d run my evaluation set to confirm quality doesn’t regress.”

That shows you can swap models safely, which matters more than which model you’re on. You already have the evaluation/ folder to back it up.

2. Back up “scalable” with specifics. Interviewers discount the word itself, but they respect the reasons behind it:

Each agent is its own A2A service, so they scale independently. Intake can run 10 replicas while Decision Support runs 2.
Agents don’t hold case state; the contextId and audit ledger do, so any replica can pick up any case.
MCP decouples agents from data, so you can swap demo stores for a real EHR or payer API without changing agent code.
On GCP, each piece maps to a managed service: Cloud Run or Agent Engine for agents, the Healthcare API for FHIR, Vertex AI for the model.
