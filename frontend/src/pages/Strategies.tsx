import { useState } from "react";
import { useNavigate } from "react-router-dom";
import StrategyCard from "../components/StrategyCard";
import StrategyEditor from "../components/StrategyEditor";
import type { SimulationParams } from "../types/simulation";
import type { Strategy } from "../types/strategy";
import { useStrategies } from "../hooks/useStrategies";

export default function Strategies() {
  const { strategies, loading, error, edit, remove } = useStrategies();
  const [editing, setEditing] = useState<Strategy | null>(null);
  const navigate = useNavigate();

  const handleRun = (strategy: Strategy) => {
    const params: SimulationParams = {
      odds_american: strategy.odds_american ?? -110,
      win_probability: strategy.win_probability ?? 0.5,
      bankroll: strategy.bankroll ?? 1000,
      bet_size: strategy.bet_size ?? 50,
      bet_size_type: (strategy.bet_size_type ?? "flat") as SimulationParams["bet_size_type"],
      num_bets: strategy.num_bets ?? 100,
      num_simulations: strategy.num_simulations ?? 5000,
    };
    navigate("/", { state: { rerunParams: params } });
  };

  return (
    <div className="p-6">
      <h1 className="mb-6 text-lg font-bold">Strategies</h1>
      {error && (
        <div role="alert" data-testid="strategies-error" className="rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
          {error}
        </div>
      )}
      {loading && <p data-testid="strategies-loading" className="text-text-muted">Loading strategies...</p>}
      {!loading && strategies.length === 0 && !error && (
        <p data-testid="strategies-empty" className="text-text-muted">
          No saved strategies yet. Save one from the Simulation workspace.
        </p>
      )}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {strategies.map((strategy) => (
          <StrategyCard
            key={strategy.id}
            strategy={strategy}
            onRun={handleRun}
            onEdit={setEditing}
            onDelete={(s) => {
              if (window.confirm(`Delete strategy "${s.name}"?`)) void remove(s.id);
            }}
          />
        ))}
      </div>
      {editing && (
        <StrategyEditor
          strategy={editing}
          onSave={(patch) => edit(editing.id, patch)}
          onCancel={() => setEditing(null)}
        />
      )}
    </div>
  );
}
