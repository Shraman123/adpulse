"""Calls an LLM to turn raw campaign data into anomaly alerts and a plain-
English daily summary, the way a media buyer would read the account.

NOTE ON PROVIDER: the spec for this project calls for the Anthropic API
(model "claude-sonnet-4-6"). This file currently calls Groq's free,
OpenAI-compatible API instead, at the project owner's request, so the app
could be fully tested end-to-end without waiting on an Anthropic key. See
README.md ("AI provider note") for the two-line swap back to Anthropic --
everything else in the app (schemas, endpoints, frontend) is provider-
agnostic and does not need to change.
"""
import json
import os
import re

from fastapi import HTTPException
from groq import Groq

from .schemas import InsightsResponse

DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL = os.environ.get("GROQ_MODEL", DEFAULT_MODEL)

SYSTEM_PROMPT = """\
You are a senior performance media buyer analyzing a multi-platform affiliate \
marketing account that runs campaigns on Google, Meta, Taboola, and TikTok. \
You are given each campaign's performance broken into four consecutive \
quarters of the selected date range (Q1 earliest -> Q4 most recent: avg daily \
spend, CTR, CPA, ROAS, conversions), plus the exact numbers for each \
campaign's single most recent day.

Your job, exactly like a sharp analyst reviewing the account before a status \
meeting with their boss, is to:

1. Spot real anomalies in the trend lines: sudden CPA spikes, CTR collapses, \
   ROAS drops, or spend that flatlines well below daily budget despite no \
   drop in performance (a pacing/lost-impression-share problem). Ignore \
   normal day-to-day noise -- only flag changes that represent a real, \
   sustained shift in a campaign's trajectory.
2. For each anomaly, give the most likely real-world cause in plain English \
   (e.g. creative fatigue, ad disapproval, audience saturation, bid too low, \
   budget cap hit, seasonality) and a concrete, specific recommendation.
3. Write a daily summary for the most recent date in the data, in the voice \
   of a media buyer briefing their boss: what changed, why it matters, and \
   what you're doing about it. Be specific with numbers. No fluff, no \
   generic filler like "continue monitoring performance."

Respond with ONLY a single JSON object, no markdown fences, no commentary, \
matching exactly this shape:

{
  "generated_for_date": "YYYY-MM-DD",
  "daily_summary": "string, 3-6 sentences",
  "anomalies": [
    {
      "platform": "Google|Meta|Taboola|TikTok",
      "campaign_id": "string",
      "campaign_name": "string",
      "severity": "high|medium|low",
      "type": "cpa_spike|ctr_collapse|pacing_miss|roas_drop|other",
      "headline": "short one-line summary of the anomaly",
      "explanation": "plain-English likely cause",
      "recommendation": "specific next action",
      "detected_around": "YYYY-MM-DD"
    }
  ]
}

If you find no real anomalies, return an empty "anomalies" array. Do not \
invent campaigns or numbers that are not implied by the data.\
"""


def _period_totals(day_rows: list[dict]) -> dict:
    spend = sum(r["spend"] for r in day_rows)
    impressions = sum(r["impressions"] for r in day_rows)
    clicks = sum(r["clicks"] for r in day_rows)
    conversions = sum(r["conversions"] for r in day_rows)
    revenue = sum(r["revenue"] for r in day_rows)
    return {
        "avg_daily_spend": spend / len(day_rows),
        "ctr_pct": (clicks / impressions * 100) if impressions else 0,
        "cpa": (spend / conversions) if conversions else 0,
        "roas": (revenue / spend) if spend else 0,
        "conversions": conversions,
    }


def _build_prompt_data(rows: list[dict]) -> str:
    """Builds a compact, token-frugal representation of the dataset: each
    campaign's trend broken into quarters (so a sustained shift is visible)
    plus the exact numbers for the most recent day (for the daily summary).
    Aggregates are spend/click/conversion weighted, not naive averages of
    ratios, so CTR/CPA/ROAS stay mathematically correct at the rollup level.
    """
    by_campaign: dict[str, list[dict]] = {}
    for r in rows:
        by_campaign.setdefault(r["campaign_id"], []).append(r)

    quarter_lines = [
        "campaign_id,campaign_name,platform,daily_budget,period,date_range,avg_daily_spend,ctr_pct,cpa,roas,conversions"
    ]
    last_day_lines = [
        "campaign_id,campaign_name,platform,daily_budget,date,spend,ctr_pct,cpa,roas,conversions"
    ]

    for campaign_id, day_rows in by_campaign.items():
        day_rows = sorted(day_rows, key=lambda r: r["date"])
        name, platform, budget = day_rows[0]["campaign_name"], day_rows[0]["platform"], day_rows[0]["daily_budget"]
        n = len(day_rows)
        edges = [0, n // 4, n // 2, (3 * n) // 4, n]
        for i in range(4):
            chunk = day_rows[edges[i]:edges[i + 1]]
            if not chunk:
                continue
            agg = _period_totals(chunk)
            date_range = f"{chunk[0]['date']}..{chunk[-1]['date']}"
            quarter_lines.append(
                f"{campaign_id},{name},{platform},{budget},Q{i + 1},{date_range},"
                f"{agg['avg_daily_spend']:.2f},{agg['ctr_pct']:.2f},{agg['cpa']:.2f},"
                f"{agg['roas']:.2f},{agg['conversions']}"
            )

        last = day_rows[-1]
        last_day_lines.append(
            f"{campaign_id},{name},{platform},{budget},{last['date']},{last['spend']:.2f},"
            f"{last['ctr'] * 100:.2f},{last['cpa']:.2f},{last['roas']:.2f},{last['conversions']}"
        )

    return (
        "SECTION 1 -- per-campaign trend by quarter of the selected date range "
        "(Q1 = earliest, Q4 = most recent; use this to spot sustained shifts):\n"
        + "\n".join(quarter_lines)
        + "\n\nSECTION 2 -- most recent day, exact numbers per campaign "
        "(use this for the daily summary):\n"
        + "\n".join(last_day_lines)
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1)
    else:
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            text = brace_match.group(0)
    return json.loads(text)


def generate_insights(rows: list[dict]) -> InsightsResponse:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not set on the server. Copy .env.example to .env and add your key.",
        )
    if not rows:
        raise HTTPException(status_code=404, detail="No campaign data available for the given filters.")

    client = Groq(api_key=api_key)
    prompt_data = _build_prompt_data(rows)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=3000,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Here is the account's performance data:\n\n{prompt_data}",
                },
            ],
        )
    except Exception as exc:  # groq SDK raises various APIError subclasses
        raise HTTPException(status_code=502, detail=f"Groq API call failed: {exc}") from exc

    raw_text = response.choices[0].message.content

    try:
        parsed = _extract_json(raw_text)
    except (json.JSONDecodeError, AttributeError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Could not parse AI response as JSON: {exc}. Raw response: {raw_text[:500]}",
        ) from exc

    parsed.setdefault("anomalies", [])
    parsed["model"] = MODEL
    return InsightsResponse(**parsed)
