import { useCallback, useEffect, useState } from "react";
import IntelligenceScore from "../components/IntelligenceScore";
import {
  buildPortfolio,
  getLatestPortfolio,
} from "../services/portfolioApi";
import type { Portfolio, PortfolioItemData } from "../types/portfolio";

const BAND_LABELS: Record<string, string> = {
  high: "High Confidence",
  medium: "Medium Confidence",
  long_shot: "Long Shot",
};

function money(value: number | null): string {
  return value === null ? "—" : `$${value.toLocaleString()}`;
}

export default function PortfolioPage() {
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [loading, setLoading] = useState(true);
  const [building, setBuilding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [bankroll, setBankroll] = useState("1000");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setPortfolio(await getLatestPortfolio());
    } catch {
      setError("Could not load the portfolio. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const handleBuild = async () => {
    setBuilding(true);
    setError(null);
    try {
      setPortfolio(await buildPortfolio(Number(bankroll)));
    } catch (err: unknown) {
      setError(
        err instanceof Error ? `Build failed. ${err.message}` : "Build failed.",
      );
    } finally {
      setBuilding(false);
    }
  };

  const byBand = (band: string) =>
    portfolio?.items.filter((i: PortfolioItemData) => i.confidence_level === band) ?? [];

  return (
    <div className="p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-lg font-bold">Portfolio</h1>
        <div className="flex items-center gap-2">
          <label htmlFor="pf-bankroll" className="text-sm text-text-secondary">
            Bankroll ($)
          </label>
          <input
            id="pf-bankroll"
            type="number"
            min={1}
            value={bankroll}
            onChange={(e) => setBankroll(e.target.value)}
            className="w-28 rounded-md border border-border bg-bg-tertiary px-3 py-1.5 text-sm text-text-primary focus:border-primary focus:outline-none"
          />
          <button
            type="button"
            data-testid="build-portfolio"
            disabled={building || Number(bankroll) <= 0}
            onClick={() => void handleBuild()}
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-bg-primary hover:bg-primary-hover disabled:opacity-50"
          >
            {building ? "Building..." : "Build Portfolio"}
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" data-testid="portfolio-error" className="mb-3 rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
          {error}
        </div>
      )}
      {loading && (
        <p data-testid="portfolio-loading" className="text-text-muted">Loading...</p>
      )}

      {!loading && !portfolio && !error && (
        <p data-testid="portfolio-empty" className="text-text-muted">
          No portfolio yet. Build one to see today's picks with confidence bands.
        </p>
      )}

      {portfolio && (
        <div data-testid="portfolio-view" className="space-y-6">
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <div className="rounded-lg border border-border bg-bg-secondary p-4">
              <p className="text-xs uppercase tracking-wide text-text-muted">Total risk</p>
              <p data-testid="pf-total-risk" className="mt-1 text-xl font-bold">
                {portfolio.total_risk ?? "—"}%
              </p>
            </div>
            <div className="rounded-lg border border-border bg-bg-secondary p-4">
              <p className="text-xs uppercase tracking-wide text-text-muted">Kelly exposure</p>
              <p data-testid="pf-kelly-exposure" className="mt-1 text-xl font-bold">
                {portfolio.kelly_exposure ?? "—"}%
              </p>
            </div>
            <div className="rounded-lg border border-border bg-bg-secondary p-4">
              <p className="text-xs uppercase tracking-wide text-text-muted">Bets</p>
              <p data-testid="pf-item-count" className="mt-1 text-xl font-bold">
                {portfolio.items.length}
              </p>
            </div>
            <div className="rounded-lg border border-border bg-bg-secondary p-4">
              <p className="text-xs uppercase tracking-wide text-text-muted">Model</p>
              <p data-testid="pf-model" className="mt-1 truncate text-xl font-bold">
                {portfolio.model_id ?? "—"}
              </p>
            </div>
          </div>

          {(Object.keys(BAND_LABELS) as string[]).map((band) => {
            const items = byBand(band);
            if (items.length === 0) return null;
            return (
              <section key={band} data-testid={`band-${band}`}>
                <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
                  {BAND_LABELS[band]} ({items.length})
                </h2>
                <div className="space-y-3">
                  {items.map((item) => (
                    <div
                      key={item.id}
                      data-testid={`portfolio-item-${item.id}`}
                      className="flex items-center justify-between rounded-lg border border-border bg-bg-secondary p-4"
                    >
                      <div>
                        <p className="font-medium text-text-primary">
                          {item.game_id ?? "—"}
                          <span className="ml-2 text-warning">
                            {"★".repeat(item.recommendation_stars ?? 0)}
                          </span>
                        </p>
                        <p className="text-xs text-text-muted">
                          Prob:{" "}
                          {item.predicted_probability === null
                            ? "—"
                            : `${(item.predicted_probability * 100).toFixed(1)}%`}{" "}
                          · EV:{" "}
                          {item.ev === null
                            ? "—"
                            : `${item.ev >= 0 ? "+" : ""}${(item.ev * 100).toFixed(1)}%`}
                        </p>
                      </div>
                      <p className="font-semibold text-primary">{money(item.stake)}</p>
                    </div>
                  ))}
                </div>
              </section>
            );
          })}

          {portfolio.items.length === 0 && (
            <p className="text-sm text-text-muted">
              No predictions scored high enough to include today.
            </p>
          )}

          <details>
            <summary className="cursor-pointer text-sm text-text-secondary hover:text-text-primary">
              How is this built?
            </summary>
            <div className="mt-3 max-w-md">
              <IntelligenceScore
                data={{
                  score: Math.max(
                    0,
                    ...portfolio.items.map((i) => (i.recommendation_stars ?? 0) * 20),
                  ),
                  stars:
                    Math.max(
                      0,
                      ...portfolio.items.map((i) => i.recommendation_stars ?? 0),
                    ) || 0,
                  risk_level:
                    (portfolio.total_risk ?? 0) > 25
                      ? "High"
                      : (portfolio.total_risk ?? 0) > 10
                        ? "Medium"
                        : "Low",
                  breakdown: {
                    allocation: { value: "bands", points: 40, max: 40 },
                    kelly: { value: "stakes", points: 35, max: 35 },
                    exposure_cap: { value: "80%", points: 25, max: 25 },
                  },
                }}
              />
              <p className="mt-2 text-xs text-text-muted">
                Summary panel — per-pick scores come from each prediction's Intelligence Score.
              </p>
            </div>
          </details>
        </div>
      )}
    </div>
  );
}
