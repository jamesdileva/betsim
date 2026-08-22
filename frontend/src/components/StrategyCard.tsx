import type { Strategy } from "../types/strategy";

interface StrategyCardProps {
  strategy: Strategy;
  onRun: (strategy: Strategy) => void;
  onEdit: (strategy: Strategy) => void;
  onDelete: (strategy: Strategy) => void;
}

function pct(value: number | null): string {
  return value === null ? "—" : `${(value * 100).toFixed(1)}%`;
}

export default function StrategyCard({ strategy, onRun, onEdit, onDelete }: StrategyCardProps) {
  return (
    <div
      data-testid={`strategy-card-${strategy.id}`}
      className="rounded-lg border border-border bg-bg-secondary p-4"
    >
      <h3 className="mb-2 font-semibold text-text-primary">{strategy.name}</h3>
      <dl className="mb-4 space-y-1 text-sm text-text-secondary">
        <div className="flex justify-between">
          <dt>Odds</dt>
          <dd data-testid={`strategy-odds-${strategy.id}`} className="text-text-primary">
            {strategy.odds_american ?? "—"}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt>Win prob</dt>
          <dd className="text-text-primary">{pct(strategy.win_probability)}</dd>
        </div>
        <div className="flex justify-between">
          <dt>Bankroll</dt>
          <dd className="text-text-primary">
            {strategy.bankroll === null ? "—" : `$${strategy.bankroll.toLocaleString()}`}
          </dd>
        </div>
        <div className="flex justify-between">
          <dt>Bet size</dt>
          <dd className="text-text-primary">
            {strategy.bet_size === null ? "—" : strategy.bet_size} ({strategy.bet_size_type})
          </dd>
        </div>
        <div className="flex justify-between">
          <dt>Bets / sims</dt>
          <dd className="text-text-primary">
            {strategy.num_bets ?? "—"} / {strategy.num_simulations ?? "—"}
          </dd>
        </div>
      </dl>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => onRun(strategy)}
          className="rounded-md bg-primary px-3 py-1.5 text-sm font-semibold text-bg-primary hover:bg-primary-hover"
        >
          Run
        </button>
        <button
          type="button"
          onClick={() => onEdit(strategy)}
          className="rounded-md border border-border px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary"
        >
          Edit
        </button>
        <button
          type="button"
          onClick={() => onDelete(strategy)}
          className="rounded-md border border-danger/50 px-3 py-1.5 text-sm text-danger hover:bg-danger/10"
        >
          Delete
        </button>
      </div>
    </div>
  );
}
