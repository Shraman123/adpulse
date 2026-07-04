import { useState } from "react";
import type { Filters, InsightsResponse } from "../types";
import { fetchInsights } from "../api";
import AnomalyCard from "./AnomalyCard";

interface Props {
  filters: Filters;
}

export default function InsightsPanel({ filters }: Props) {
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchInsights(filters);
      setInsights(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate insights.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-200">AI Insights</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Analyzes the currently filtered data like a media buyer reviewing the account.
          </p>
        </div>
        <button
          onClick={runAnalysis}
          disabled={loading}
          className="shrink-0 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Analyzing…" : insights ? "Re-run analysis" : "Generate insights"}
        </button>
      </div>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/40 p-3 text-sm text-red-700 dark:text-red-300">
          {error}
        </div>
      )}

      {!error && !insights && !loading && (
        <p className="text-sm text-gray-400 italic">No analysis yet. Click "Generate insights" to run the AI analyst.</p>
      )}

      {insights && (
        <div className="flex flex-col gap-4">
          <div className="rounded-md bg-gray-50 dark:bg-gray-800 p-3">
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
              Daily summary — {insights.generated_for_date}
            </p>
            <p className="text-sm text-gray-800 dark:text-gray-100 whitespace-pre-line">{insights.daily_summary}</p>
          </div>

          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2">
              {insights.anomalies.length} anomal{insights.anomalies.length === 1 ? "y" : "ies"} flagged
            </p>
            <div className="flex flex-col gap-3">
              {insights.anomalies.map((a, i) => (
                <AnomalyCard key={`${a.campaign_id ?? a.campaign_name}-${i}`} anomaly={a} />
              ))}
            </div>
          </div>

          <p className="text-[11px] text-gray-400">Model: {insights.model}</p>
        </div>
      )}
    </div>
  );
}
