import { americanToImpliedProb } from "../types/simulation";
import { kellyFraction } from "../utils/kelly";

interface KellyCalculatorProps {
  oddsAmerican: number | null;
  winProbability: number | null;
}

export default function KellyCalculator({ oddsAmerican, winProbability }: KellyCalculatorProps) {
  if (oddsAmerican === null || winProbability === null) return null;
  const fraction = kellyFraction(oddsAmerican, winProbability);
  const edge = winProbability - americanToImpliedProb(oddsAmerican);
  return (
    <div data-testid="kelly-calculator" className="rounded-md border border-border bg-bg-tertiary p-3 text-sm">
      <p className="text-text-secondary">
        Kelly fraction:{" "}
        <span data-testid="kelly-fraction" className="font-semibold text-text-primary">
          {(fraction * 100).toFixed(2)}%
        </span>{" "}
        of bankroll
        <span className="text-text-muted"> (half-Kelly: {(fraction * 50).toFixed(2)}%)</span>
      </p>
      <p className={`mt-0.5 text-xs ${edge > 0 ? "text-success" : "text-danger"}`}>
        {edge > 0 ? `Edge: +${(edge * 100).toFixed(1)}%` : "No edge at these odds — Kelly says don't bet."}
      </p>
    </div>
  );
}
