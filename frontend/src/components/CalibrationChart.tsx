import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CalibrationReport } from "../types/systemPlays";

const GRID_COLOR = "#334155";
const AXIS_COLOR = "#94a3b8";

interface CalibrationChartProps {
  report: CalibrationReport;
  /** Fixed dimensions for testing environments without layout support. */
  width?: number;
  height?: number;
}

export default function CalibrationChart({ report, width, height }: CalibrationChartProps) {
  const data = [
    { name: "Stated", probability: +(report.stated_probability * 100).toFixed(2) },
    { name: "Actual (simulated)", probability: +(report.actual_win_rate * 100).toFixed(2) },
  ];
  const sizeProps = width !== undefined && height !== undefined ? { width, height } : {};
  const chart = (
    <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 8 }} {...sizeProps}>
      <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" />
      <XAxis dataKey="name" stroke={AXIS_COLOR} tick={{ fill: AXIS_COLOR, fontSize: 12 }} />
      <YAxis
        domain={[0, 100]}
        stroke={AXIS_COLOR}
        tick={{ fill: AXIS_COLOR, fontSize: 12 }}
        tickFormatter={(v: number) => `${v}%`}
      />
      <Tooltip
        cursor={{ fill: "#33415555" }}
        contentStyle={{
          backgroundColor: "#1e293b",
          border: "1px solid #475569",
          borderRadius: 8,
          color: "#f8fafc",
        }}
        formatter={(value) => [`${Number(value ?? 0).toFixed(2)}%`, "Probability"]}
      />
      {/* band around the actual rate: +/- the tolerance implied by the CI */}
      <ReferenceLine
        y={+(report.actual_win_rate * 100).toFixed(2)}
        stroke="#a78bfa"
        strokeDasharray="4 4"
        label={{ value: "actual", fill: AXIS_COLOR, fontSize: 10, position: "insideTopRight" }}
      />
      <Bar dataKey="probability" name="Probability" fill="#60a5fa" radius={[4, 4, 0, 0]} isAnimationActive={false} />
    </BarChart>
  );

  return (
    <div data-testid="calibration-chart">
      <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
        Stated vs. actual probability
      </h3>
      {width !== undefined && height !== undefined ? (
        chart
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          {chart}
        </ResponsiveContainer>
      )}
    </div>
  );
}
