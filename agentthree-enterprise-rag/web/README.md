# AgentThree Enterprise RAG · React console

Local Live Ask UI over the FastAPI backend. Zero cloud / LLM cost.

```bash
# Terminal 1 — API
cd ..
source .venv/bin/activate   # after pip install -e ".[dev]"
agentthree-rag serve

# Terminal 2 — Vite
cd web
yarn install    # or: npm install
yarn dev
```

Open http://127.0.0.1:5173 (`/api` is proxied to `http://127.0.0.1:8765`).

```bash
yarn build   # outputs web/dist — served at / when the API restarts
```
