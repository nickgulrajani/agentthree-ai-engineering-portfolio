# 60-second demo

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
agentthree-finops demo
```

Expected:

1. **See** — $412.8k/mo, 61% tagged, $2.58 per 1k card transactions.
2. **Allocate** — applying the tag standard locally moves coverage to 91%.
3. **Guard** — `deny_untagged.json` **FAIL**; `allow_tagged.json` **PASS**.
4. **Optimize** — all recs selected → $324.8k run rate, $2.03 unit cost.

Then open the storyboard:

```bash
agentthree-finops serve
```

No AWS credentials. No cloud spend.
