import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ResultsHistoryTable from "../components/ResultsHistoryTable";
import { deleteRun, listRuns } from "../services/strategiesApi";
import type { SimulationParams } from "../types/simulation";
import type { RunSummary } from "../types/strategy";

export default function ResultsHistory() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRuns(await listRuns(100));
    } catch {
      setError("Could not load history. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const handleRerun = (run: RunSummary) => {
    if (run.odds_american === null || run.win_probability === null) return;
    const params: SimulationParams = {
      odds_american: run.odds_american,
      win_probability: run.win_probability,
      bankroll: run.bankroll ?? 1000,
      bet_size: run.bet_size ?? 50,
      bet_size_type: (run.bet_size_type ?? "flat") as SimulationParams["bet_size_type"],
      num_bets: run.num_bets ?? 100,
      num_simulations: run.num_simulations ?? 5000,
    };
    navigate("/", { state: { rerunParams: params } });
  };

  const handleDelete = async (run: RunSummary) => {
    if (!window.confirm("Delete this simulation run from history?")) return;
    try {
      await deleteRun(run.run_id);
      setRuns((prev) => prev.filter((r) => r.run_id !== run.run_id));
    } catch {
      setError("Could not delete the run.");
    }
  };

  return (
    <div className="p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-lg font-bold">Results History</h1>
        <button
          type="button"
          onClick={() => void refresh()}
          className="rounded-md border border-border px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary"
        >
          Refresh
        </button>
      </div>
      {error && (
        <div role="alert" data-testid="history-error" className="mb-3 rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
          {error}
        </div>
      )}
      {loading ? (
        <p data-testid="history-loading" className="text-text-muted">Loading history...</p>
      ) : (
        <ResultsHistoryTable runs={runs} onRerun={handleRerun} onDelete={(r) => void handleDelete(r)} />
      )}
    </div>
  );
}
