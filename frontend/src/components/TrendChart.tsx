import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChartPoint } from "../aggregate";
import { SERIES_COLORS } from "../colors";

interface Props {
  title: string;
  data: ChartPoint[];
  seriesKeys: string[];
  valuePrefix?: string;
  valueSuffix?: string;
}

export default function TrendChart({ title, data, seriesKeys, valuePrefix = "", valueSuffix = "" }: Props) {
  const formatValue = (v: number | string | undefined) =>
    `${valuePrefix}${Number(v ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}${valueSuffix}`;

  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-200 mb-2">{title}</h3>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 5, right: 12, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-700" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11 }}
            tickFormatter={(d: string) => d.slice(5)}
            minTickGap={20}
          />
          <YAxis tick={{ fontSize: 11 }} tickFormatter={(v: number) => formatValue(v)} width={70} />
          <Tooltip formatter={(value) => formatValue(value as number)} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
          {seriesKeys.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
          {seriesKeys.map((key, i) => (
            <Line
              key={key}
              type="monotone"
              dataKey={key}
              stroke={SERIES_COLORS[i % SERIES_COLORS.length]}
              dot={false}
              strokeWidth={2}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
