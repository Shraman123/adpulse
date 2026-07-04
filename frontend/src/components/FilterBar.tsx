import type { Filters, MetaResponse } from "../types";

interface Props {
  meta: MetaResponse | null;
  filters: Filters;
  onChange: (filters: Filters) => void;
}

export default function FilterBar({ meta, filters, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-end gap-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Platform</label>
        <select
          className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-1.5 text-sm"
          value={filters.platform}
          onChange={(e) => onChange({ ...filters, platform: e.target.value })}
        >
          <option value="All">All platforms</option>
          {meta?.platforms.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-500 dark:text-gray-400">Start date</label>
        <input
          type="date"
          className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-1.5 text-sm"
          value={filters.start_date}
          min={meta?.start_date ?? undefined}
          max={filters.end_date}
          onChange={(e) => onChange({ ...filters, start_date: e.target.value })}
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-500 dark:text-gray-400">End date</label>
        <input
          type="date"
          className="rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-3 py-1.5 text-sm"
          value={filters.end_date}
          min={filters.start_date}
          max={meta?.end_date ?? undefined}
          onChange={(e) => onChange({ ...filters, end_date: e.target.value })}
        />
      </div>

      {meta && (
        <button
          className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
          onClick={() => onChange({ platform: "All", start_date: meta.start_date!, end_date: meta.end_date! })}
        >
          Reset filters
        </button>
      )}
    </div>
  );
}
