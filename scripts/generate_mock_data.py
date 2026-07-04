"""
Generates a synthetic 30-day performance dataset for AdPulse across four
platforms (Google, Meta, Taboola, TikTok). Deterministic (seeded) so the
dataset -- and the three anomalies baked into it -- are stable across runs.

Run:
    python scripts/generate_mock_data.py

Output:
    data/campaigns.json
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

NUM_DAYS = 30
START_DATE = date(2026, 6, 5)  # day 1 .. day 30

OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "campaigns.json"

# ---------------------------------------------------------------------------
# Campaign roster. Each campaign gets a baseline daily spend/CTR/CVR/AOV that
# the generator wobbles day to day with noise, then three campaigns get a
# scripted anomaly layered on top starting at a specific day index (0-based).
# ---------------------------------------------------------------------------

CAMPAIGNS = [
    # Google
    dict(id="goog-1", platform="Google", name="Search - Brand", daily_budget=300,
         base_spend=280, ctr=0.065, cvr=0.09, aov=120, cpc_hint=1.8),
    dict(id="goog-2", platform="Google", name="Search - Nonbrand", daily_budget=450,
         base_spend=420, ctr=0.032, cvr=0.045, aov=110, cpc_hint=2.6),
    dict(id="goog-3", platform="Google", name="Shopping - Core", daily_budget=400,
         base_spend=370, ctr=0.021, cvr=0.06, aov=95, cpc_hint=1.1),
    dict(id="goog-4", platform="Google", name="Shopping - Prospecting", daily_budget=600,
         base_spend=560, ctr=0.018, cvr=0.035, aov=90, cpc_hint=1.3),
    dict(id="goog-5", platform="Google", name="PMax - Full Funnel", daily_budget=500,
         base_spend=470, ctr=0.024, cvr=0.05, aov=105, cpc_hint=1.5),
    dict(id="goog-6", platform="Google", name="Display - Retargeting", daily_budget=200,
         base_spend=170, ctr=0.012, cvr=0.04, aov=100, cpc_hint=0.7),

    # Meta
    dict(id="meta-1", platform="Meta", name="Prospecting - Broad", daily_budget=350,
         base_spend=330, ctr=0.014, cvr=0.055, aov=85, cpc_hint=1.4),
    dict(id="meta-2", platform="Meta", name="Prospecting - LAL 1%", daily_budget=300,
         base_spend=280, ctr=0.016, cvr=0.06, aov=88, cpc_hint=1.3),
    dict(id="meta-3", platform="Meta", name="Retargeting - Cart Abandoners", daily_budget=150,
         base_spend=140, ctr=0.028, cvr=0.12, aov=95, cpc_hint=1.0),
    dict(id="meta-4", platform="Meta", name="Retargeting - Engaged 30d", daily_budget=150,
         base_spend=135, ctr=0.024, cvr=0.10, aov=92, cpc_hint=0.95),
    dict(id="meta-5", platform="Meta", name="Advantage+ Shopping", daily_budget=500,
         base_spend=470, ctr=0.019, cvr=0.05, aov=100, cpc_hint=1.2),
    dict(id="meta-6", platform="Meta", name="UGC Video - Cold", daily_budget=400,
         base_spend=375, ctr=0.017, cvr=0.048, aov=90, cpc_hint=1.25),

    # Taboola
    dict(id="tab-1", platform="Taboola", name="Native - Homepage Feed", daily_budget=250,
         base_spend=230, ctr=0.006, cvr=0.03, aov=80, cpc_hint=0.45),
    dict(id="tab-2", platform="Taboola", name="Native - Content Recirc", daily_budget=200,
         base_spend=185, ctr=0.005, cvr=0.028, aov=78, cpc_hint=0.4),
    dict(id="tab-3", platform="Taboola", name="Native - Advertorial A", daily_budget=300,
         base_spend=270, ctr=0.007, cvr=0.035, aov=82, cpc_hint=0.5),
    dict(id="tab-4", platform="Taboola", name="Native - Advertorial B", daily_budget=300,
         base_spend=275, ctr=0.0065, cvr=0.032, aov=80, cpc_hint=0.48),
    dict(id="tab-5", platform="Taboola", name="Native - Mobile Feed", daily_budget=180,
         base_spend=165, ctr=0.0055, cvr=0.027, aov=76, cpc_hint=0.42),

    # TikTok
    dict(id="tt-1", platform="TikTok", name="Spark Ads - Creator 1", daily_budget=350,
         base_spend=330, ctr=0.021, cvr=0.05, aov=70, cpc_hint=0.9),
    dict(id="tt-2", platform="TikTok", name="In-Feed - Broad", daily_budget=400,
         base_spend=375, ctr=0.019, cvr=0.045, aov=68, cpc_hint=0.95),
    dict(id="tt-3", platform="TikTok", name="In-Feed - Interest Stack", daily_budget=300,
         base_spend=280, ctr=0.017, cvr=0.042, aov=70, cpc_hint=0.92),
    dict(id="tt-4", platform="TikTok", name="Spark Ads - Creator 2", daily_budget=250,
         base_spend=235, ctr=0.020, cvr=0.048, aov=72, cpc_hint=0.88),
    dict(id="tt-5", platform="TikTok", name="TopView - Launch", daily_budget=200,
         base_spend=180, ctr=0.023, cvr=0.05, aov=75, cpc_hint=1.05),
]

# Anomaly configuration (0-based day index within the 30-day window)
META_CPA_SPIKE_CAMPAIGN = "meta-6"     # UGC Video - Cold, creative fatigue
META_CPA_SPIKE_START = 19              # ~day 20

TIKTOK_CTR_COLLAPSE_CAMPAIGN = "tt-2"  # In-Feed - Broad, ad disapproval
TIKTOK_CTR_COLLAPSE_DAY = 14           # ~day 15

GOOGLE_PACING_MISS_CAMPAIGN = "goog-4"  # Shopping - Prospecting, bid too low
GOOGLE_PACING_MISS_START = 17            # ~day 18


def noisy(value, pct=0.08):
    return max(0.0, value * (1 + random.uniform(-pct, pct)))


def build_day(campaign, day_idx):
    spend = noisy(campaign["base_spend"])
    ctr = noisy(campaign["ctr"], 0.12)
    cvr = noisy(campaign["cvr"], 0.15)
    aov = noisy(campaign["aov"], 0.05)

    # --- Scripted anomalies -------------------------------------------------
    if campaign["id"] == META_CPA_SPIKE_CAMPAIGN and day_idx >= META_CPA_SPIKE_START:
        # Creative fatigue: CTR and CVR decay progressively, spend held flat
        # by automated bidding trying to hit volume goals -> CPA climbs hard.
        days_in = day_idx - META_CPA_SPIKE_START + 1
        decay = min(0.75, 0.10 * days_in)
        ctr *= (1 - decay)
        cvr *= (1 - decay * 0.9)
        spend = noisy(campaign["base_spend"] * (1 + 0.05 * days_in), 0.06)

    if campaign["id"] == TIKTOK_CTR_COLLAPSE_CAMPAIGN and day_idx >= TIKTOK_CTR_COLLAPSE_DAY:
        # Ad disapproval / audience saturation: CTR craters overnight and
        # stays low; delivery (impressions) also throttles somewhat.
        ctr *= 0.16
        cvr *= 0.5
        spend = noisy(campaign["base_spend"] * 0.7, 0.1)

    if campaign["id"] == GOOGLE_PACING_MISS_CAMPAIGN and day_idx >= GOOGLE_PACING_MISS_START:
        # Bid too low -> lost impression share: spend flatlines well below
        # budget even though nothing else about the campaign changed.
        spend = noisy(campaign["daily_budget"] * 0.32, 0.05)

    # Impressions derived from spend and an implied CPM (keeps CTR the driver
    # of clicks rather than back-solving impressions from CPC).
    implied_cpm = noisy(18.0, 0.15)
    impressions = int(max(500, spend / implied_cpm * 1000))
    clicks = max(0, round(impressions * ctr))
    conversions = max(0, round(clicks * cvr))
    revenue = round(conversions * aov, 2)

    return {
        "date": (START_DATE + timedelta(days=day_idx)).isoformat(),
        "day_index": day_idx + 1,
        "platform": campaign["platform"],
        "campaign_id": campaign["id"],
        "campaign_name": campaign["name"],
        "daily_budget": campaign["daily_budget"],
        "spend": round(spend, 2),
        "impressions": impressions,
        "clicks": int(clicks),
        "ctr": round((clicks / impressions) if impressions else 0, 4),
        "conversions": int(conversions),
        "cpa": round((spend / conversions) if conversions else 0, 2),
        "revenue": revenue,
        "roas": round((revenue / spend) if spend else 0, 3),
    }


def generate():
    rows = []
    for campaign in CAMPAIGNS:
        for day_idx in range(NUM_DAYS):
            rows.append(build_day(campaign, day_idx))
    return rows


def main():
    rows = generate()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    print(f"Wrote {len(rows)} rows ({len(CAMPAIGNS)} campaigns x {NUM_DAYS} days) to {OUT_PATH}")


if __name__ == "__main__":
    main()
