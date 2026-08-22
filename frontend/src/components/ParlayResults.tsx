import type { MetricSummary } from "../types/simulation";
import DistributionChart from "./DistributionChart";

export interface ParlayResultsProps {
  combinedProbability: number;
  combinedDecimalOdds: number;
  evPerUnit: number;
  breakEvenProbability: number;
  metrics: MetricSummary;
  distribution: { bin_edges: number[]; counts: number[] };
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function ParlayResults(props: ParlayResultsProps) {
  const {
    combinedProbability,
    combinedDecimalOdds,
    evPerUnit,
    breakEvenProbability,
    metrics,
    distribution,
  } = props;

  const cards = [
    { label: "Combined probability", value: pct(combinedProbability), testId: "parlay-probability" },
    { label: "Combined payout", value: `${combinedDecimalOdds.toFixed(2)}x`, testId: "parlay-payout" },
    {
      label: "EV per unit",
      value: `${evPerUnit >= 0 ? "+" : ""}${(evPerUnit * 100).toFixed(1)}%`,
      testId: "parlay-ev",
      className: evPerUnit >= 0 ? "text-success" : "text-danger",
    },
    { label: "Break-even prob", value: pct(breakEvenProbability), testId: "parlay-break-even" },
    {
      label: "Risk of ruin",
      value: pct(metrics.risk_of_ruin),
      testId: "parlay-ruin",
      className: metrics.risk_of_ruin > 0.25 ? "text-danger" : undefined,
    },
    {
      label: "Avg ending bankroll",
      value: `$${Math.round(metrics.avg_ending_bankroll).toLocaleString()}`,
      testId: "parlay-avg-final",
    },
  ];

  return (
    <div data-testid="parlay-results" className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
        {cards.map((card) => (
          <div key={card.label} className="rounded-lg border border-border bg-bg-secondary p-4">
            <p className="text-xs uppercase tracking-wide text-text-muted">{card.label}</p>
            <p data-testid={card.testId} className={`mt-1 text-xl font-bold ${card.className ?? ""}`}>
              {card.value}
            </p>
          </div>
        ))}
      </div>

      {evPerUnit < 0 && (
        <p role="status" data-testid="parlay-warning" className="text-sm text-danger">
          This parlay has negative EV ({pct(evPerUnit)}). You need{" "}
          {(breakEvenProbability * 100).toFixed(1)}% per leg on average to break even — parlays
          multiply variance faster than edge.
        </p>
      )}

      {metrics.risk_of_ruin > 0.5 && (
        <p role="status" data-testid="parlay-ruin-warning" className="text-sm text-danger">
          You go broke in more than half of simulations at this bet size.
        </p>
      )}

      <DistributionChart distribution={distribution} />
    </div>
  );
}
