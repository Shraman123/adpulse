# AdPulse

An AI-powered media buying performance dashboard for an affiliate marketing team running campaigns across Google, Meta, Taboola, and TikTok. Includes an AI insight agent that reads the account's performance data and produces plain-English anomaly alerts and a daily summary, like a media buyer briefing their boss.

## 1. What does this tool do?

AdPulse gives a media buying team one dashboard instead of four. It shows spend, CPA, ROAS, and CTR trends across all campaigns on Google, Meta, Taboola, and TikTok, filterable by platform and date range.

On top of that, an "AI Insights" panel sends the account's performance data to an LLM and gets back two things a human analyst would normally have to produce by hand:

- **Flagged anomalies** — specific campaigns with a real, sustained problem (a CPA spike, a CTR collapse, a budget pacing miss), each with a plain-English guess at the likely cause (creative fatigue, ad disapproval, bid too low, etc.) and a concrete recommendation.
- **A daily summary** written in the voice of a media buyer reporting to their boss: what changed, why it matters, what to do about it.

The mock dataset (30 days x 22 campaigns across the four platforms) has three anomalies deliberately seeded into it so the AI has something real to catch:

1. A CPA spike on a Meta campaign starting ~day 20 (creative fatigue — CTR and conversion rate decay while spend holds steady).
2. A CTR collapse on a TikTok campaign around day 15 (ad disapproval / audience saturation — CTR craters overnight and stays low).
3. A budget pacing miss on a Google campaign — spend flatlines well below its daily budget despite no drop in performance (bid too low / lost impression share).

## 2. Why did you build THIS one?

It's Today Media runs affiliate campaigns at scale across Google, Meta, Taboola, and TikTok. Each of those platforms has its own dashboard, its own UI, and its own definition of "CTR" — and none of them talk to each other. That means a media buyer's actual workflow is manually cross-checking four disconnected tabs every day just to answer "is anything broken?" That process is slow, and worse, it's error-prone: a slow CPA creep on one Meta campaign, or a CTR collapse on one TikTok campaign, can sit unnoticed for days inside a single platform's dashboard before anyone happens to look at the right chart on the right day. At scale, across dozens of campaigns, that's real money leaking out through inattention, not strategy.

I built this to attack that specific gap: one account-wide view, plus an AI layer that does the pattern-matching a tired human eye would miss at 6pm on a Friday — not a fixed set of threshold rules, but an LLM given the actual trend data and asked to reason about what's a real anomaly versus normal noise, and to explain *why* in plain English rather than just flashing a red number. That's the difference between "CPA is up 340%" (which any dashboard can already show you) and "this looks like creative fatigue on your cold-traffic campaign, here's what to do about it" — the second one is what actually saves a media buyer time and catches the leak before it costs real budget.

## 3. What would you build next if this were a full-time job?

- **Real API connectors to Google, Meta, Taboola, and TikTok, wired through MCP.** Replace the mock dataset with live pulls from each platform's reporting API, exposed as MCP tools/servers so the same AI agent (and other agents/tools) can query live account data directly instead of a static JSON file.
- **Slack alerting.** Push high-severity anomalies into a Slack channel the moment they're detected, instead of requiring someone to open the dashboard and click "Generate insights."
- **Automated budget reallocation recommendations.** Once the agent can see ROAS/CPA trends across the whole account, the natural next step is recommending (and eventually, with approval, executing) budget shifts — pull spend from an underperforming campaign into one that's scaling efficiently — rather than just flagging problems after the fact.

Further out: campaign-level creative fatigue prediction (catch it before CTR collapses, not after), a proper time-series anomaly-detection layer feeding the LLM so it isn't reasoning over raw noise, and multi-day/week-over-week digest emails.

---

## AI provider note

This build calls **Groq's free, OpenAI-compatible API** (model `llama-3.3-70b-versatile`) rather than a paid provider — it's free, fast, and was enough to get a fully live, real end-to-end demo running rather than one that just claims it would work with a key.

The LLM call is isolated to a single file, `backend/insights.py` — everything else (schemas, endpoints, frontend) is provider-agnostic. Swapping to Anthropic's Claude (or OpenAI, or anything else) is a contained change:

1. `pip install anthropic`.
2. In `backend/insights.py`, replace the `Groq` client with `anthropic.Anthropic`, swap `client.chat.completions.create(...)` for `client.messages.create(...)` (moving `SYSTEM_PROMPT` to the `system=` kwarg), and read the response text from `response.content[0].text` instead of `response.choices[0].message.content`.
3. Set `ANTHROPIC_API_KEY` (and `ANTHROPIC_MODEL`, e.g. a current Claude Sonnet model) instead of `GROQ_API_KEY`/`GROQ_MODEL`.

Note on data volume: `insights.py` sends a compact, quarter-aggregated summary per campaign (not 660 raw daily rows) specifically to stay under Groq's free-tier tokens-per-minute limit (12,000 TPM on `llama-3.3-70b-versatile`). A paid provider's limits are much higher, so swapping would let you send more granular daily detail for finer-grained anomaly dating.

## Project structure

```
AdPulse/
├── api/index.py          # Vercel serverless entrypoint (imports the FastAPI app)
├── backend/
│   ├── main.py            # FastAPI app + routes
│   ├── data_loader.py      # Loads/filters the mock dataset
│   ├── insights.py         # LLM call: builds prompt, parses response
│   └── schemas.py          # Pydantic response models
├── data/campaigns.json    # Generated mock dataset (committed, so it's reproducible)
├── scripts/generate_mock_data.py  # Regenerates data/campaigns.json (seeded, deterministic)
├── frontend/               # React + TypeScript + Tailwind + Recharts (Vite)
├── requirements.txt
├── vercel.json
└── .env.example
```

## Running locally

**Backend:**

```bash
python -m venv .venv
.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

cp .env.example .env      # then fill in GROQ_API_KEY

uvicorn backend.main:app --reload --port 8000
```

**Frontend** (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server (`http://localhost:5173`) proxies `/api/*` to the backend at `http://127.0.0.1:8000` (see `frontend/vite.config.ts`), so just open `http://localhost:5173`.

**Regenerating the mock dataset** (optional — a seeded copy is already committed at `data/campaigns.json`):

```bash
python scripts/generate_mock_data.py
```

## Deploying to Vercel

This repo is set up to deploy as a single Vercel project: the FastAPI app as a Python serverless function (`api/index.py`), the React app as a static build, wired together in `vercel.json`.

1. Push this repo to GitHub (or run `vercel` from the CLI directly).
2. Import it in Vercel, or run `vercel` from the project root.
3. In the Vercel project's Environment Variables settings, add `GROQ_API_KEY` (and `GROQ_MODEL` if you want to override the default).
4. Deploy. `vercel.json` handles routing `/api/*` to the Python function and everything else to the built frontend — no other config needed.
