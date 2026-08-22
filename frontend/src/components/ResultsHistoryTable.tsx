import { useMemo, useState } from "react";
import type { RunSummary } from "../types/strategy";

interface ResultsHistoryTableProps {
  runs: RunSummary[];
  onRerun: (run: RunSummary) => void;
  onDelete: (run: RunSummary) => void;
}

function pct(value: number | null): string {
  return value === null ? "—" : `${(value * 100).toFixed(1)}%`;
}

function money(value: number | null): string {
  return value === null ? "—" : `$${Math.round(value).toLocaleString()}`;
}

export default function ResultsHistoryTable({ runs, onRerun, onDelete }: ResultsHistoryTableProps) {
  const [filter, setFilter] = useState("");

  const filtered = useMemo(() => {
    if (!filter.trim()) return runs;
    const q = filter.trim().toLowerCase();
    return runs.filter((run) =>
      [run.odds_american, run.win_probability, run.bet_size_type, run.created_at]
        .some((field) => String(field ?? "").toLowerCase().includes(q)),
    );
  }, [runs, filter]);

  return (
    <div data-testid="results-history-table">
      <input
        aria-label="Filter history"
        placeholder="Filter by odds, probability, strategy..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        className="mb-3 w-full max-w-sm rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none"
      />
      {filtered.length === 0 ? (
        <p className="text-text-muted" data-testid="history-empty">
          No simulation runs found.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-text-muted">
                <th scope="col" className="py-2 pr-4">Date</th>
                <th scope="col" className="py-2 pr-4">Odds</th>
                <th scope="col" className="py-2 pr-4">Win prob</th>
                <th scope="col" className="py-2 pr-4">Strategy</th>
                <th scope="col" className="py-2 pr-4">Bets</th>
                <th scope="col" className="py-2 pr-4">Sims</th>
                <th scope="col" className="py-2 pr-4">Win %</th>
                <th scope="col" className="py-2 pr-4">Avg final</th>
                <th scope="col" className="py-2 pr-4">Ruin %</th>
                <th scope="col" className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((run) => (
                <tr key={run.run_id} data-testid={`history-row-${run.run_id}`} className="border-b border-border last:border-b-0">
                  <td className="py-2 pr-4 text-text-secondary">
                    {run.created_at ? new Date(run.created_at).toLocaleString() : "—"}
                  </td>
                  <td className="py-2 pr-4">{run.odds_american ?? "—"}</td>
                  <td className="py-2 pr-4">{pct(run.win_probability)}</td>
                  <td className="py-2 pr-4">{run.bet_size_type ?? "—"}</td>
                  <td className="py-2 pr-4">{run.num_bets ?? "—"}</td>
                  <td className="py-2 pr-4">{run.result_count}</td>
                  <td className="py-2 pr-4">{pct(run.win_pct)}</td>
                  <td className="py-2 pr-4">{money(run.avg_final_bankroll)}</td>
                  <td className={`py-2 pr-4 ${run.risk_of_ruin !== null && run.risk_of_ruin > 0.25 ? "text-danger" : ""}`}>
                    {pct(run.risk_of_ruin)}
                  </td>
                  <td className="py-2">
                    <button
                      type="button"
                      onClick={() => onRerun(run)}
                      className="mr-2 rounded-md bg-primary px-2.5 py-1 text-xs font-semibold text-bg-primary hover:bg-primary-hover"
                    >
                      Re-run
                    </button>
                    <button
                      type="button"
                      onClick={() => onDelete(run)}
                      className="rounded-md border border-danger/50 px-2.5 py-1 text-xs text-danger hover:bg-danger/10"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
