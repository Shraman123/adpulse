"""Loads the mock campaign dataset and provides simple filtering helpers."""
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "campaigns.json"


@lru_cache(maxsize=1)
def load_data() -> list[dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_data(
    platform: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    rows = load_data()
    if platform and platform.lower() != "all":
        rows = [r for r in rows if r["platform"].lower() == platform.lower()]
    if start_date:
        rows = [r for r in rows if r["date"] >= start_date]
    if end_date:
        rows = [r for r in rows if r["date"] <= end_date]
    return rows


def get_meta() -> dict:
    rows = load_data()
    platforms = sorted({r["platform"] for r in rows})
    campaigns = sorted(
        {(r["platform"], r["campaign_id"], r["campaign_name"]) for r in rows},
        key=lambda t: (t[0], t[2]),
    )
    dates = sorted({r["date"] for r in rows})
    return {
        "platforms": platforms,
        "campaigns": [
            {"platform": p, "campaign_id": cid, "campaign_name": name}
            for p, cid, name in campaigns
        ],
        "start_date": dates[0] if dates else None,
        "end_date": dates[-1] if dates else None,
    }
