import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DistributionData } from "../types/simulation";
import { buildDistributionData } from "../utils/chartData";

const GRID_COLOR = "#334155";
const AXIS_COLOR = "#94a3b8";

interface DistributionChartProps {
  distribution: DistributionData;
  /** Fixed dimensions for testing environments without layout support. */
  width?: number;
  height?: number;
}

export default function DistributionChart({ distribution, width, height }: DistributionChartProps) {
  const data = buildDistributionData(distribution);
  const sizeProps = width !== undefined && height !== undefined ? { width, height } : {};
  const chart = (
    <BarChart data={data} margin={{ top: 8, right: 16, bottom: 24, left: 8 }} {...sizeProps}>
          <CartesianGrid stroke={GRID_COLOR} strokeDasharray="3 3" />
          <XAxis
            dataKey="label"
            stroke={AXIS_COLOR}
            tick={{ fill: AXIS_COLOR, fontSize: 10 }}
            interval="preserveStartEnd"
            angle={-35}
            textAnchor="end"
          />
          <YAxis
            stroke={AXIS_COLOR}
            tick={{ fill: AXIS_COLOR, fontSize: 12 }}
            allowDecimals={false}
          />
          <Tooltip
            cursor={{ fill: "#33415555" }}
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              borderRadius: 8,
              color: "#f8fafc",
            }}
            formatter={(value) => [`${Number(value ?? 0).toLocaleString()} runs`, "Simulations"]}
          />
          <Bar dataKey="count" name="Simulations" fill="#60a5fa" radius={[4, 4, 0, 0]} isAnimationActive={false} />
    </BarChart>
  );

  return (
    <div data-testid="distribution-chart">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
        Final bankroll distribution
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
