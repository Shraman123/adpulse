import { useMemo } from "react";
import type { CampaignRow, Filters } from "../types";
import { buildSeries, summarize } from "../aggregate";
import TrendChart from "./TrendChart";

interface Props {
  rows: CampaignRow[];
  filters: Filters;
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-gray-900 dark:text-gray-50">{value}</p>
    </div>
  );
}

export default function Dashboard({ rows, filters }: Props) {
  const groupBy = filters.platform === "All" ? "platform" : "campaign_name";

  const spendSeries = useMemo(() => buildSeries(rows, "spend", groupBy), [rows, groupBy]);
  const cpaSeries = useMemo(() => buildSeries(rows, "cpa", groupBy), [rows, groupBy]);
  const roasSeries = useMemo(() => buildSeries(rows, "roas", groupBy), [rows, groupBy]);
  const ctrSeries = useMemo(() => buildSeries(rows, "ctr", groupBy), [rows, groupBy]);
  const stats = useMemo(() => summarize(rows), [rows]);

  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 dark:border-gray-700 p-8 text-center text-sm text-gray-500">
        No data for the selected filters.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard label="Total spend" value={`$${stats.totalSpend.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} />
        <StatCard label="Blended CPA" value={`$${stats.avgCpa.toFixed(2)}`} />
        <StatCard label="Blended ROAS" value={`${stats.avgRoas.toFixed(2)}x`} />
        <StatCard label="Blended CTR" value={`${stats.avgCtr.toFixed(2)}%`} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <TrendChart title="Spend" data={spendSeries.data} seriesKeys={spendSeries.seriesKeys} valuePrefix="$" />
        <TrendChart title="CPA" data={cpaSeries.data} seriesKeys={cpaSeries.seriesKeys} valuePrefix="$" />
        <TrendChart title="ROAS" data={roasSeries.data} seriesKeys={roasSeries.seriesKeys} valueSuffix="x" />
        <TrendChart title="CTR" data={ctrSeries.data} seriesKeys={ctrSeries.seriesKeys} valueSuffix="%" />
      </div>
    </div>
  );
}
