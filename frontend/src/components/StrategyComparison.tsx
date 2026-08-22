import { useCallback, useEffect, useMemo, useState } from "react";
import api from "../services/api";
import type { SimulationParams, SimulationResult } from "../types/simulation";
import type { BetSizeType } from "../types/simulation";

const STRATEGIES: { value: BetSizeType; label: string }[] = [
  { value: "flat", label: "Flat $" },
  { value: "percentage", label: "% of bankroll" },
  { value: "kelly", label: "Kelly" },
  { value: "half_kelly", label: "Half-Kelly" },
];

interface ComparisonRow {
  strategy: string;
  winPct: number;
  avgFinal: number;
  medianFinal: number;
  riskOfRuin: number;
}

interface StrategyComparisonProps {
  params: SimulationParams | null;
}

export default function StrategyComparison({ params }: StrategyComparisonProps) {
  const [rows, setRows] = useState<ComparisonRow[] | null>(null);
  const [running, setRunning] = useState(false);

  const run = useCallback(async (baseParams: SimulationParams) => {
    setRunning(true);
    setRows(null);
    try {
      const results = await Promise.all(
        STRATEGIES.map(async (s) => {
          const response = await api.post<SimulationResult>("/api/simulate", {
            ...baseParams,
            bet_size_type: s.value,
          });
          return { strategy: s.label, result: response.data };
        }),
      );
      setRows(
        results.map(({ strategy, result }) => ({
          strategy,
          winPct: result.metrics.win_pct,
          avgFinal: result.metrics.avg_ending_bankroll,
          medianFinal: result.metrics.median_ending_bankroll,
          riskOfRuin: result.metrics.risk_of_ruin,
        })),
      );
    } finally {
      setRunning(false);
    }
  }, []);

  useEffect(() => {
    if (params) void run(params);
  }, [params, run]);

  const warning = useMemo(() => {
    if (!rows) return false;
    return rows.some((row) => row.medianFinal < params!.bankroll * 0.5);
  }, [rows, params]);

  if (!params) return null;

  return (
    <div data-testid="strategy-comparison" className="mt-6">
      <div className="mb-2 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-text-muted">
          Bankroll strategy comparison
        </h2>
        <button
          type="button"
          data-testid="comparison-rerun"
          disabled={running}
          onClick={() => void run(params)}
          className="rounded-md border border-border px-3 py-1 text-xs text-text-secondary hover:text-text-primary disabled:opacity-50"
        >
          {running ? "Comparing..." : "Re-compare"}
        </button>
      </div>

      {running && (
        <p role="status" data-testid="comparison-loading" className="text-text-muted">
          Running all four strategies...
        </p>
      )}

      {rows && (
        <>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-text-muted">
                <th scope="col" className="py-2 pr-4">Strategy</th>
                <th scope="col" className="py-2 pr-4">Win %</th>
                <th scope="col" className="py-2 pr-4">Avg final</th>
                <th scope="col" className="py-2 pr-4">Median final</th>
                <th scope="col" className="py-2">Ruin %</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.strategy} data-testid={`comparison-${row.strategy}`} className="border-b border-border last:border-b-0">
                  <td className="py-2 pr-4 font-medium">{row.strategy}</td>
                  <td className="py-2 pr-4">{(row.winPct * 100).toFixed(1)}%</td>
                  <td className="py-2 pr-4">${Math.round(row.avgFinal).toLocaleString()}</td>
                  <td className={`py-2 pr-4 ${row.medianFinal < params.bankroll * 0.5 ? "text-danger" : ""}`}>
                    ${Math.round(row.medianFinal).toLocaleString()}
                  </td>
                  <td className={`py-2 ${row.riskOfRuin > 0.25 ? "text-danger" : ""}`}>
                    {(row.riskOfRuin * 100).toFixed(1)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {warning && (
            <p role="status" data-testid="comparison-warning" className="mt-3 text-sm text-warning">
              At least one strategy leaves you with less than half your starting bankroll in a
              typical run.
            </p>
          )}
        </>
      )}
    </div>
  );
}
