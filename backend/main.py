"""AdPulse FastAPI app: serves mock campaign data and AI-generated insights."""
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .data_loader import filter_data, get_meta
from .insights import generate_insights
from .schemas import CampaignRow, InsightsResponse

app = FastAPI(title="AdPulse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/meta")
def meta() -> dict:
    """Available platforms, campaigns, and date range -- used to populate filters."""
    return get_meta()


@app.get("/api/campaigns", response_model=list[CampaignRow])
def campaigns(
    platform: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> list[dict]:
    return filter_data(platform=platform, start_date=start_date, end_date=end_date)


@app.post("/api/insights", response_model=InsightsResponse)
def insights(
    platform: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> InsightsResponse:
    """Runs the AI analyst over the (optionally filtered) dataset and returns
    flagged anomalies plus a plain-English daily summary."""
    rows = filter_data(platform=platform, start_date=start_date, end_date=end_date)
    if not rows:
        raise HTTPException(status_code=404, detail="No campaign data available for the given filters.")
    return generate_insights(rows)
