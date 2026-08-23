import type { IntelligenceScoreData } from "../types/portfolio";

interface IntelligenceScoreProps {
  data: IntelligenceScoreData;
}

const BAND_COLORS: Record<string, string> = {
  Low: "text-success",
  Medium: "text-warning",
  High: "text-danger",
};

export default function IntelligenceScore({ data }: IntelligenceScoreProps) {
  const entries = Object.entries(data.breakdown).filter(([key]) => key !== "bonuses");
  return (
    <div
      data-testid="intelligence-score"
      className="rounded-lg border border-border bg-bg-secondary p-4"
    >
      <div className="flex items-baseline justify-between">
        <h3 className="font-semibold text-text-primary">Intelligence Score</h3>
        <p className="text-2xl font-bold text-primary">
          <span data-testid="score-value">{data.score}</span>
          <span className="text-sm font-normal text-text-muted">/100</span>
        </p>
      </div>
      <p className="mt-0.5 text-xs text-text-muted">
        {"★".repeat(data.stars)}
        {"☆".repeat(5 - data.stars)} · Risk:{" "}
        <span
          data-testid="score-risk"
          className={BAND_COLORS[data.risk_level] ?? "text-text-secondary"}
        >
          {data.risk_level}
        </span>
      </p>

      <ul className="mt-3 space-y-1.5">
        {entries.map(([name, entry]) => (
          <li key={name} data-testid={`score-component-${name}`} className="text-sm">
            <div className="flex items-center justify-between">
              <span className="capitalize text-text-secondary">{name}</span>
              <span className="text-text-primary">
                {typeof entry.value === "number" ? (entry.value * 100).toFixed(1) + "%" : String(entry.value)}
                {""}
                {" "}
                → {entry.points}/{entry.max}
              </span>
            </div>
            <div className="mt-0.5 h-1.5 w-full rounded bg-bg-tertiary">
              <div
                className="h-1.5 rounded bg-primary"
                style={{ width: `${Math.min(100, (entry.points / entry.max) * 100)}%` }}
              />
            </div>
          </li>
        ))}
        {data.breakdown.bonuses && (
          <li className="pt-1 text-xs text-text-muted" data-testid="score-bonuses">
            Bonuses: {String(data.breakdown.bonuses.applied)} (+{data.breakdown.bonuses.points})
          </li>
        )}
      </ul>
    </div>
  );
}
