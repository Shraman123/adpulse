import type { Anomaly } from "../types";

const SEVERITY_STYLES: Record<Anomaly["severity"], string> = {
  high: "border-red-300 bg-red-50 dark:border-red-800 dark:bg-red-950/40",
  medium: "border-amber-300 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/40",
  low: "border-gray-300 bg-gray-50 dark:border-gray-700 dark:bg-gray-800/40",
};

const SEVERITY_BADGE: Record<Anomaly["severity"], string> = {
  high: "bg-red-600 text-white",
  medium: "bg-amber-500 text-white",
  low: "bg-gray-500 text-white",
};

export default function AnomalyCard({ anomaly }: { anomaly: Anomaly }) {
  return (
    <div className={`rounded-lg border p-4 ${SEVERITY_STYLES[anomaly.severity]}`}>
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span className={`rounded px-2 py-0.5 text-[11px] font-semibold uppercase ${SEVERITY_BADGE[anomaly.severity]}`}>
          {anomaly.severity}
        </span>
        <span className="rounded bg-gray-200 dark:bg-gray-700 px-2 py-0.5 text-[11px] font-medium text-gray-700 dark:text-gray-200">
          {anomaly.platform}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400">{anomaly.campaign_name}</span>
        {anomaly.detected_around && (
          <span className="ml-auto text-[11px] text-gray-400">since ~{anomaly.detected_around}</span>
        )}
      </div>
      <p className="font-semibold text-gray-900 dark:text-gray-50">{anomaly.headline}</p>
      <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{anomaly.explanation}</p>
      <p className="mt-2 text-sm">
        <span className="font-medium text-gray-900 dark:text-gray-100">Recommendation: </span>
        <span className="text-gray-700 dark:text-gray-300">{anomaly.recommendation}</span>
      </p>
    </div>
  );
}
