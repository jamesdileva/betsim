import { useState } from "react";
import type { Strategy } from "../types/strategy";

interface StrategyEditorProps {
  strategy: Strategy;
  onSave: (patch: StrategyPatch) => Promise<unknown>;
  onCancel: () => void;
}

type StrategyPatch = Partial<{
  name: string;
  odds_american: number;
  win_probability: number;
  bankroll: number;
  bet_size: number;
  bet_size_type: string;
  num_bets: number;
  num_simulations: number;
}>;

const inputClass =
  "w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none";
const labelClass = "mb-1 block text-xs text-text-secondary";

export default function StrategyEditor({ strategy, onSave, onCancel }: StrategyEditorProps) {
  const [form, setForm] = useState({
    name: strategy.name,
    odds_american: String(strategy.odds_american ?? ""),
    win_probability_pct: String((strategy.win_probability ?? 0) * 100),
    bankroll: String(strategy.bankroll ?? ""),
    bet_size: String(strategy.bet_size ?? ""),
    bet_size_type: strategy.bet_size_type ?? "flat",
    num_bets: String(strategy.num_bets ?? ""),
    num_simulations: String(strategy.num_simulations ?? ""),
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof form) => (value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError(null);
    try {
      await onSave({
        name: form.name,
        odds_american: Number(form.odds_american),
        win_probability: Number(form.win_probability_pct) / 100,
        bankroll: Number(form.bankroll),
        bet_size: Number(form.bet_size),
        bet_size_type: form.bet_size_type,
        num_bets: Number(form.num_bets),
        num_simulations: Number(form.num_simulations),
      });
      onCancel();
    } catch {
      setError("Could not save changes.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={`Edit ${strategy.name}`}
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 p-4"
    >
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md space-y-3 rounded-lg border border-border bg-bg-secondary p-5"
      >
        <h2 className="text-lg font-bold">Edit strategy</h2>
        <div>
          <label htmlFor="edit-name" className={labelClass}>Name</label>
          <input id="edit-name" value={form.name} onChange={(e) => set("name")(e.target.value)} className={inputClass} required />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="edit-odds" className={labelClass}>Odds</label>
            <input id="edit-odds" type="number" value={form.odds_american} onChange={(e) => set("odds_american")(e.target.value)} className={inputClass} />
          </div>
          <div>
            <label htmlFor="edit-prob" className={labelClass}>Win prob (%)</label>
            <input id="edit-prob" type="number" value={form.win_probability_pct} onChange={(e) => set("win_probability_pct")(e.target.value)} className={inputClass} />
          </div>
          <div>
            <label htmlFor="edit-bankroll" className={labelClass}>Bankroll</label>
            <input id="edit-bankroll" type="number" value={form.bankroll} onChange={(e) => set("bankroll")(e.target.value)} className={inputClass} />
          </div>
          <div>
            <label htmlFor="edit-bet-size" className={labelClass}>Bet size</label>
            <input id="edit-bet-size" type="number" value={form.bet_size} onChange={(e) => set("bet_size")(e.target.value)} className={inputClass} />
          </div>
          <div>
            <label htmlFor="edit-type" className={labelClass}>Strategy type</label>
            <select id="edit-type" value={form.bet_size_type} onChange={(e) => set("bet_size_type")(e.target.value)} className={inputClass}>
              <option value="flat">Flat $</option>
              <option value="percentage">% of bankroll</option>
              <option value="kelly">Kelly</option>
              <option value="half_kelly">Half Kelly</option>
            </select>
          </div>
          <div>
            <label htmlFor="edit-num-bets" className={labelClass}>Bets per run</label>
            <input id="edit-num-bets" type="number" value={form.num_bets} onChange={(e) => set("num_bets")(e.target.value)} className={inputClass} />
          </div>
        </div>
        {error && <p role="alert" className="text-sm text-danger">{error}</p>}
        <div className="flex justify-end gap-2 pt-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md border border-border px-4 py-2 text-sm text-text-secondary hover:text-text-primary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={saving}
            className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-bg-primary hover:bg-primary-hover disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}
