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
import type { TrajectoryBands } from "../types/simulation";
import { buildTrajectoryData } from "../utils/chartData";

const GRID_COLOR = "#334155";
const AXIS_COLOR = "#94a3b8";

interface BankrollChartProps {
  bands: TrajectoryBands;
  /** Fixed dimensions for testing environments without layout support. */
  width?: number;
  height?: number;
}

export default function BankrollChart({ bands, width, height }: BankrollChartProps) {
  const data = buildTrajectoryData(bands);
  const sizeProps = width !== undefined && height !== undefined ? { width, height } : {};
  const chart = (
    <LineChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }} {...sizeProps}>
          <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" />
          <XAxis
            dataKey="bet"
            stroke={AXIS_COLOR}
            tick={{ fill: AXIS_COLOR, fontSize: 12 }}
            label={{ value: "Bet #", position: "insideBottomRight", offset: -4, fill: AXIS_COLOR }}
          />
          <YAxis
            stroke={AXIS_COLOR}
            tick={{ fill: AXIS_COLOR, fontSize: 12 }}
            tickFormatter={(v: number) => `$${Math.round(v)}`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              borderRadius: 8,
              color: "#f8fafc",
            }}
            labelFormatter={(label) => `After bet ${String(label)}`}
            formatter={(value) => `$${Number(value ?? 0).toLocaleString()}`}
          />
          <Legend wrapperStyle={{ color: AXIS_COLOR }} />
          <Line
            type="monotone"
            dataKey="min"
            name="Worst"
            stroke="#334155"
            strokeWidth={1}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="max"
            name="Best"
            stroke="#334155"
            strokeWidth={1}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="p10"
            name="10th pct"
            stroke="#60a5fa"
            strokeOpacity={0.45}
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="p90"
            name="90th pct"
            stroke="#a78bfa"
            strokeOpacity={0.45}
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
          <Line
            type="monotone"
            dataKey="median"
            name="Median"
            stroke="#60a5fa"
            strokeWidth={2.5}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
  );

  return (
    <div data-testid="bankroll-chart">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
        Bankroll trajectory
      </h2>
      {width !== undefined && height !== undefined ? (
        chart
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          {chart}
        </ResponsiveContainer>
      )}
    </div>
  );
}
