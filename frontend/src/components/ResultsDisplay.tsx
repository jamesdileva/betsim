import type { MetricSummary } from "../types/simulation";

function formatMoney(value: number): string {
  return value.toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
}

function riskColor(risk: number): string {
  if (risk < 0.1) return "text-success";
  if (risk <= 0.25) return "text-warning";
  return "text-danger";
}

interface ResultsDisplayProps {
  metrics: MetricSummary;
}

export default function ResultsDisplay({ metrics }: ResultsDisplayProps) {
  const cards = [
    {
      label: "Win %",
      value: `${(metrics.win_pct * 100).toFixed(1)}%`,
      testId: "metric-win-pct",
    },
    {
      label: "Avg ending bankroll",
      value: formatMoney(metrics.avg_ending_bankroll),
      testId: "metric-avg-bankroll",
    },
    {
      label: "Risk of ruin",
      value: `${(metrics.risk_of_ruin * 100).toFixed(1)}%`,
      testId: "metric-risk-of-ruin",
      className: riskColor(metrics.risk_of_ruin),
    },
    {
      label: "EV per bet",
      value: `${metrics.ev_per_bet >= 0 ? "+" : ""}${metrics.ev_per_bet.toFixed(2)}`,
      testId: "metric-ev-per-bet",
      className: metrics.ev_per_bet >= 0 ? "text-success" : "text-danger",
    },
  ];

  return (
    <section aria-label="Simulation results">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map((card) => (
          <div
            key={card.label}
            className="rounded-lg border border-border bg-bg-secondary p-4"
          >
            <p className="text-xs uppercase tracking-wide text-text-muted">{card.label}</p>
            <p data-testid={card.testId} className={`mt-1 text-2xl font-bold ${card.className ?? ""}`}>
              {card.value}
            </p>
          </div>
        ))}
      </div>
      {metrics.risk_of_ruin > 0.25 && (
        <p role="status" data-testid="ruin-warning" className="mt-3 text-sm text-danger">
          This strategy is aggressive — you go broke in more than a quarter of simulations.
        </p>
      )}
    </section>
  );
}
