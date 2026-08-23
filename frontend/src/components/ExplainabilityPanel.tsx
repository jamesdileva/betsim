import type { Factor } from "../types/ml";

interface ExplainabilityPanelProps {
  factors: Factor[];
  confidence?: number | null;
}

/**
 * Shows the top factors behind a prediction with +/- indicators
 * (positive = pushes probability up, negative = down) and the model's
 * self-reported confidence when available.
 */
export default function ExplainabilityPanel({ factors, confidence }: ExplainabilityPanelProps) {
  return (
    <div data-testid="explainability-panel" className="rounded-lg border border-border bg-bg-secondary p-4">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-text-muted">
          Top factors
        </h3>
        {confidence !== null && confidence !== undefined && (
          <span data-testid="model-confidence" className="text-xs text-text-secondary">
            Model confidence:{" "}
            <span className="font-semibold text-text-primary">
              {(confidence * 100).toFixed(0)}%
            </span>
          </span>
        )}
      </div>

      {factors.length === 0 ? (
        <p className="text-sm text-text-muted">No factor data available for this prediction.</p>
      ) : (
        <ul className="space-y-1.5">
          {factors.map((factor) => (
            <li
              key={factor.feature}
              data-testid={`factor-${factor.feature}`}
              className="flex items-center justify-between text-sm"
            >
              <span className="text-text-secondary">
                <span
                  aria-hidden="true"
                  className={`mr-2 font-bold ${factor.direction === "+" ? "text-success" : "text-danger"}`}
                >
                  {factor.direction}
                </span>
                {factor.label}
              </span>
              <span
                className={`font-medium ${
                  factor.impact >= 0 ? "text-success" : "text-danger"
                }`}
              >
                {factor.impact >= 0 ? "+" : ""}
                {(factor.impact * 100).toFixed(1)}%
              </span>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-3 text-xs text-text-muted">
        Heuristic attribution — not derived from a trained model yet.
      </p>
    </div>
  );
}
