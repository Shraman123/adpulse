export interface CampaignRow {
  date: string;
  day_index: number;
  platform: string;
  campaign_id: string;
  campaign_name: string;
  daily_budget: number;
  spend: number;
  impressions: number;
  clicks: number;
  ctr: number;
  conversions: number;
  cpa: number;
  revenue: number;
  roas: number;
}

export interface CampaignMeta {
  platform: string;
  campaign_id: string;
  campaign_name: string;
}

export interface MetaResponse {
  platforms: string[];
  campaigns: CampaignMeta[];
  start_date: string | null;
  end_date: string | null;
}

export type AnomalySeverity = "high" | "medium" | "low";
export type AnomalyType = "cpa_spike" | "ctr_collapse" | "pacing_miss" | "roas_drop" | "other";

export interface Anomaly {
  platform: string;
  campaign_id?: string | null;
  campaign_name: string;
  severity: AnomalySeverity;
  type: AnomalyType;
  headline: string;
  explanation: string;
  recommendation: string;
  detected_around?: string | null;
}

export interface InsightsResponse {
  generated_for_date: string;
  daily_summary: string;
  anomalies: Anomaly[];
  model: string;
}

export interface Filters {
  platform: string; // "All" or a platform name
  start_date: string;
  end_date: string;
}
