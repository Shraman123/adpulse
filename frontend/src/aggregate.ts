import type { CampaignRow } from "./types";

export type ChartMetric = "spend" | "cpa" | "roas" | "ctr";

/** One row per date, one numeric key per series (platform or campaign name). */
export type ChartPoint = { date: string } & Record<string, number | string>;

interface Totals {
  spend: number;
  impressions: number;
  clicks: number;
  conversions: number;
  revenue: number;
}

function emptyTotals(): Totals {
  return { spend: 0, impressions: 0, clicks: 0, conversions: 0, revenue: 0 };
}

function deriveMetric(totals: Totals, metric: ChartMetric): number {
  switch (metric) {
    case "spend":
      return totals.spend;
    case "cpa":
      return totals.conversions ? totals.spend / totals.conversions : 0;
    case "roas":
      return totals.spend ? totals.revenue / totals.spend : 0;
    case "ctr":
      return totals.impressions ? (totals.clicks / totals.impressions) * 100 : 0;
  }
}

/**
 * Pivots raw campaign rows into a wide, per-date series suitable for
 * Recharts: grouped by platform when no single platform is selected
 * (so the account view stays readable), or by campaign when it is.
 */
export function buildSeries(
  rows: CampaignRow[],
  metric: ChartMetric,
  groupBy: "platform" | "campaign_name"
): { data: ChartPoint[]; seriesKeys: string[] } {
  const byDate = new Map<string, Map<string, Totals>>();
  const seriesKeySet = new Set<string>();

  for (const row of rows) {
    const key = groupBy === "platform" ? row.platform : row.campaign_name;
    seriesKeySet.add(key);

    if (!byDate.has(row.date)) byDate.set(row.date, new Map());
    const groups = byDate.get(row.date)!;
    if (!groups.has(key)) groups.set(key, emptyTotals());
    const totals = groups.get(key)!;

    totals.spend += row.spend;
    totals.impressions += row.impressions;
    totals.clicks += row.clicks;
    totals.conversions += row.conversions;
    totals.revenue += row.revenue;
  }

  const seriesKeys = Array.from(seriesKeySet).sort();
  const data: ChartPoint[] = Array.from(byDate.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, groups]) => {
      const point: ChartPoint = { date };
      for (const key of seriesKeys) {
        const totals = groups.get(key);
        point[key] = totals ? Number(deriveMetric(totals, metric).toFixed(4)) : 0;
      }
      return point;
    });

  return { data, seriesKeys };
}

export interface SummaryStats {
  totalSpend: number;
  avgCpa: number;
  avgRoas: number;
  avgCtr: number;
}

export function summarize(rows: CampaignRow[]): SummaryStats {
  const totals = rows.reduce((acc, r) => {
    acc.spend += r.spend;
    acc.impressions += r.impressions;
    acc.clicks += r.clicks;
    acc.conversions += r.conversions;
    acc.revenue += r.revenue;
    return acc;
  }, emptyTotals());

  return {
    totalSpend: totals.spend,
    avgCpa: totals.conversions ? totals.spend / totals.conversions : 0,
    avgRoas: totals.spend ? totals.revenue / totals.spend : 0,
    avgCtr: totals.impressions ? (totals.clicks / totals.impressions) * 100 : 0,
  };
}
