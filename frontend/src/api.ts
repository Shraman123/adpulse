import type { CampaignRow, Filters, InsightsResponse, MetaResponse } from "./types";

async function parseOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // response body wasn't JSON; fall back to statusText
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

function filterParams(filters: Partial<Filters>): string {
  const params = new URLSearchParams();
  if (filters.platform && filters.platform !== "All") params.set("platform", filters.platform);
  if (filters.start_date) params.set("start_date", filters.start_date);
  if (filters.end_date) params.set("end_date", filters.end_date);
  return params.toString();
}

export async function fetchMeta(): Promise<MetaResponse> {
  const res = await fetch("/api/meta");
  return parseOrThrow<MetaResponse>(res);
}

export async function fetchCampaigns(filters: Partial<Filters>): Promise<CampaignRow[]> {
  const res = await fetch(`/api/campaigns?${filterParams(filters)}`);
  return parseOrThrow<CampaignRow[]>(res);
}

export async function fetchInsights(filters: Partial<Filters>): Promise<InsightsResponse> {
  const res = await fetch(`/api/insights?${filterParams(filters)}`, { method: "POST" });
  return parseOrThrow<InsightsResponse>(res);
}
