"""Pydantic response models for the AdPulse API."""
from typing import Optional

from pydantic import BaseModel


class CampaignRow(BaseModel):
    date: str
    day_index: int
    platform: str
    campaign_id: str
    campaign_name: str
    daily_budget: float
    spend: float
    impressions: int
    clicks: int
    ctr: float
    conversions: int
    cpa: float
    revenue: float
    roas: float


class Anomaly(BaseModel):
    platform: str
    campaign_id: Optional[str] = None
    campaign_name: str
    severity: str  # "high" | "medium" | "low"
    type: str  # "cpa_spike" | "ctr_collapse" | "pacing_miss" | "other"
    headline: str
    explanation: str
    recommendation: str
    detected_around: Optional[str] = None


class InsightsResponse(BaseModel):
    generated_for_date: str
    daily_summary: str
    anomalies: list[Anomaly]
    model: str
