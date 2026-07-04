import { useEffect, useState } from "react";
import type { CampaignRow, Filters, MetaResponse } from "./types";
import { fetchCampaigns, fetchMeta } from "./api";
import FilterBar from "./components/FilterBar";
import Dashboard from "./components/Dashboard";
import InsightsPanel from "./components/InsightsPanel";

export default function App() {
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [filters, setFilters] = useState<Filters | null>(null);
  const [rows, setRows] = useState<CampaignRow[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMeta()
      .then((m) => {
        setMeta(m);
        setFilters({ platform: "All", start_date: m.start_date ?? "", end_date: m.end_date ?? "" });
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load app metadata."));
  }, []);

  useEffect(() => {
    if (!filters) return;
    fetchCampaigns(filters)
      .then(setRows)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load campaign data."));
  }, [filters]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <header className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
        <div className="mx-auto max-w-6xl px-4 py-4">
          <h1 className="text-xl font-bold text-gray-900 dark:text-gray-50">AdPulse</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Media buying performance dashboard — Google, Meta, Taboola, TikTok
          </p>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 flex flex-col gap-6">
        {error && (
          <div className="rounded-md border border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/40 p-3 text-sm text-red-700 dark:text-red-300">
            {error}
          </div>
        )}

        {filters && <FilterBar meta={meta} filters={filters} onChange={setFilters} />}
        {filters && <Dashboard rows={rows} filters={filters} />}
        {filters && <InsightsPanel filters={filters} />}
      </main>
    </div>
  );
}
