import { useCallback, useEffect, useState } from "react";
import { getPerformance, runBacktests } from "../services/analyticsApi";
import type { PerformanceResponse } from "../types/analytics";

function pct(value: number | null): string {
  return value === null ? "—" : `${(value * 100).toFixed(1)}%`;
}

export default function Analytics() {
  const [data, setData] = useState<PerformanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [lastRun, setLastRun] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setData(await getPerformance());
    } catch {
      setError("Could not load analytics. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleRunBacktests = async () => {
    setRunning(true);
    setLastRun(null);
    try {
      const response = await runBacktests();
      setLastRun(`${response.backtests_created} backtests recorded.`);
      await refresh();
    } catch {
      setLastRun(null);
      setError("Backtest run failed.");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold">Analytics</h1>
        <div className="flex items-center gap-3">
          {lastRun && (
            <span role="status" data-testid="analytics-last-run" className="text-xs text-success">
              {lastRun}
            </span>
          )}
          <button
            type="button"
            data-testid="run-backtests"
            disabled={running}
            onClick={() => void handleRunBacktests()}
            className="rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-bg-primary hover:bg-primary-hover disabled:opacity-50"
          >
            {running ? "Replaying..." : "Run Backtests"}
          </button>
        </div>
      </div>

      {error && (
        <div role="alert" data-testid="analytics-error" className="mb-3 rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
          {error}
        </div>
      )}
      {loading && (
        <p data-testid="analytics-loading" className="text-text-muted">
          Loading performance...
        </p>
      )}

      {!loading && data && (
        <>
          {data.summary.length === 0 ? (
            <p data-testid="analytics-empty" className="text-text-muted">
              No backtested predictions yet. Predictions become backtestable once their games have
              final scores.
            </p>
          ) : (
            <table className="w-full max-w-2xl text-sm" data-testid="analytics-summary-table">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-text-muted">
                  <th scope="col" className="py-2 pr-4">Model</th>
                  <th scope="col" className="py-2 pr-4">Backtested</th>
                  <th scope="col" className="py-2 pr-4">Accuracy</th>
                  <th scope="col" className="py-2">Avg ROI (Kelly)</th>
                </tr>
              </thead>
              <tbody>
                {data.summary.map((row) => (
                  <tr key={row.model_id} data-testid={`summary-${row.model_id}`} className="border-b border-border last:border-b-0">
                    <td className="py-2 pr-4 font-medium">{row.model_id}</td>
                    <td className="py-2 pr-4">{row.backtest_count}</td>
                    <td className={`py-2 pr-4 ${row.accuracy !== null && row.accuracy < 0.5 ? "text-danger" : ""}`}>
                      {pct(row.accuracy)}
                    </td>
                    <td className={`py-2 ${(row.avg_roi ?? 0) < 0 ? "text-danger" : "text-success"}`}>
                      {row.avg_roi === null ? "—" : `${(row.avg_roi * 100).toFixed(2)}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {Object.entries(data.evaluations).map(([modelId, evaluations]) =>
            evaluations.length > 0 ? (
              <div key={modelId} className="mt-8" data-testid={`evaluations-${modelId}`}>
                <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-text-muted">
                  Evaluation history — {modelId}
                </h2>
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-text-muted">
                      <th scope="col" className="py-2 pr-4">Evaluated</th>
                      <th scope="col" className="py-2 pr-4">Accuracy</th>
                      <th scope="col" className="py-2 pr-4">Calibration err</th>
                      <th scope="col" className="py-2 pr-4">Brier</th>
                      <th scope="col" className="py-2">Avg ROI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evaluations.map((e) => (
                      <tr key={e.id} className="border-b border-border last:border-b-0">
                        <td className="py-2 pr-4 text-text-secondary">
                          {e.evaluated_at ? new Date(e.evaluated_at).toLocaleString() : "—"}
                        </td>
                        <td className="py-2 pr-4">{pct(e.accuracy)}</td>
                        <td className="py-2 pr-4">{pct(e.calibration_error)}</td>
                        <td className="py-2 pr-4">{e.brier_score?.toFixed(4) ?? "—"}</td>
                        <td className="py-2">
                          {e.avg_roi === null ? "—" : `${(e.avg_roi * 100).toFixed(2)}%`}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null,
          )}
        </>
      )}
    </div>
  );
}
