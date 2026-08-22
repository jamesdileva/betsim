import type { MetricSummary } from "../types/simulation";

function money(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
}

interface MetricsTableProps {
  metrics: MetricSummary;
}

export default function MetricsTable({ metrics }: MetricsTableProps) {
  const rows: { label: string; value: string; testId?: string; danger?: boolean }[] = [
    { label: "Median ending bankroll", value: money(metrics.median_ending_bankroll), testId: "table-median" },
    { label: "Best case", value: money(metrics.max_bankroll), testId: "table-best-case" },
    { label: "Worst case", value: money(metrics.min_bankroll), testId: "table-worst-case" },
    { label: "Std deviation", value: money(metrics.std_dev), testId: "table-std-dev" },
    {
      label: "Avg max drawdown",
      value: money(metrics.avg_max_drawdown),
      testId: "table-avg-drawdown",
      danger: true,
    },
    {
      label: "Worst drawdown",
      value: money(metrics.worst_case_drawdown),
      testId: "table-worst-drawdown",
      danger: true,
    },
    {
      label: "EV total (all bets)",
      value: `${metrics.ev_total >= 0 ? "+" : ""}${money(metrics.ev_total)}`,
      testId: "table-ev-total",
      danger: metrics.ev_total < 0,
    },
  ];

  return (
    <div data-testid="metrics-table">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
        Detailed metrics
      </h2>
      <table className="w-full text-sm">
        <tbody>
          {rows.map((row) => (
            <tr key={row.label} className="border-b border-border last:border-b-0">
              <td className="py-2 pr-4 text-text-secondary">{row.label}</td>
              <td
                data-testid={row.testId}
                className={`py-2 text-right font-medium ${
                  row.danger ? "text-danger" : "text-text-primary"
                }`}
              >
                {row.value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
