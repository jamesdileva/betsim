import { useEffect, useMemo, useState } from "react";
import type { SimulationParams } from "../types/simulation";
import { americanToImpliedProb } from "../types/simulation";

export const BET_SIZE_TYPES = [
  { value: "flat", label: "Flat $" },
  { value: "percentage", label: "% of bankroll" },
  { value: "kelly", label: "Kelly" },
  { value: "half_kelly", label: "Half Kelly" },
] as const;

interface FormState {
  oddsAmerican: string;
  winProbabilityPct: string;
  bankroll: string;
  betSize: string;
  betSizeType: string;
  numBets: string;
  numSimulations: string;
}

export interface FormValues {
  oddsAmerican?: number;
  winProbabilityPct?: number;
  bankroll?: number;
  betSize?: number;
  betSizeType?: string;
  numBets?: number;
  numSimulations?: number;
}

interface SimulationFormProps {
  defaults?: Partial<Pick<SimulationParams, "bankroll" | "num_bets" | "num_simulations">>;
  initialValues?: FormValues | null;
  onRun: (params: SimulationParams) => void;
}

function validate(state: FormState): Record<string, string> {
  const errors: Record<string, string> = {};
  const odds = Number(state.oddsAmerican);
  if (!state.oddsAmerican || Number.isNaN(odds) || odds === 0 || Math.abs(odds) < 100) {
    errors.odds = "Odds must be a nonzero American value like -110 or +150.";
  }
  const prob = Number(state.winProbabilityPct);
  if (!state.winProbabilityPct || Number.isNaN(prob) || prob <= 0 || prob >= 100) {
    errors.winProbability = "Win probability must be between 0% and 100%.";
  }
  const bankroll = Number(state.bankroll);
  if (!state.bankroll || Number.isNaN(bankroll) || bankroll <= 0) {
    errors.bankroll = "Bankroll must be greater than $0.";
  }
  const betSize = Number(state.betSize);
  if (
    !state.betSize ||
    Number.isNaN(betSize) ||
    (betSize <= 0 && state.betSizeType !== "kelly" && state.betSizeType !== "half_kelly")
  ) {
    errors.betSize = "Bet size must be greater than zero for this strategy.";
  }
  const numBets = Number(state.numBets);
  if (!Number.isInteger(numBets) || numBets < 1 || numBets > 10_000) {
    errors.numBets = "Bets per run must be an integer from 1 to 10,000.";
  }
  const sims = Number(state.numSimulations);
  if (!Number.isInteger(sims) || sims < 100 || sims > 100_000) {
    errors.numSimulations = "Simulations must be an integer from 100 to 100,000.";
  }
  return errors;
}

function stateFrom(
  defaults?: SimulationFormProps["defaults"],
  initialValues?: FormValues | null,
): FormState {
  const base: FormState = {
    oddsAmerican: "-110",
    winProbabilityPct: "55",
    bankroll: String(defaults?.bankroll ?? 1000),
    betSize: "50",
    betSizeType: "flat",
    numBets: String(defaults?.num_bets ?? 100),
    numSimulations: String(defaults?.num_simulations ?? 5000),
  };
  if (!initialValues) return base;
  const apply = (key: keyof FormState, value: number | string | undefined) => {
    if (value !== undefined) base[key] = String(value);
  };
  apply("oddsAmerican", initialValues.oddsAmerican);
  apply("winProbabilityPct", initialValues.winProbabilityPct);
  apply("bankroll", initialValues.bankroll);
  apply("betSize", initialValues.betSize);
  if (initialValues.betSizeType) base.betSizeType = initialValues.betSizeType;
  apply("numBets", initialValues.numBets);
  apply("numSimulations", initialValues.numSimulations);
  return base;
}

export default function SimulationForm({ defaults, initialValues, onRun }: SimulationFormProps) {
  const [state, setState] = useState<FormState>(() => stateFrom(defaults, initialValues));
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    if (!initialValues) return;
    // merge semantics: only keys present on initialValues are applied, so a
    // live-odds pick can change just the odds while scenarios set everything
    setState((prev) => {
      const next = { ...prev };
      const apply = (key: keyof FormState, value: number | string | undefined) => {
        if (value !== undefined) next[key] = String(value);
      };
      apply("oddsAmerican", initialValues.oddsAmerican);
      apply("winProbabilityPct", initialValues.winProbabilityPct);
      apply("bankroll", initialValues.bankroll);
      apply("betSize", initialValues.betSize);
      if (initialValues.betSizeType) next.betSizeType = initialValues.betSizeType;
      apply("numBets", initialValues.numBets);
      apply("numSimulations", initialValues.numSimulations);
      return next;
    });
    setErrors({});
     
  }, [initialValues]);

  const impliedProb = useMemo(() => {
    const odds = Number(state.oddsAmerican);
    if (Number.isNaN(odds) || odds === 0 || Math.abs(odds) < 100) return null;
    return americanToImpliedProb(odds);
  }, [state.oddsAmerican]);

  const set = (key: keyof FormState) => (value: string) =>
    setState((prev) => ({ ...prev, [key]: value }));

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    const nextErrors = validate(state);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;
    onRun({
      odds_american: Number(state.oddsAmerican),
      win_probability: Number(state.winProbabilityPct) / 100,
      bankroll: Number(state.bankroll),
      bet_size: Number(state.betSize),
      bet_size_type: state.betSizeType as SimulationParams["bet_size_type"],
      num_bets: Number(state.numBets),
      num_simulations: Number(state.numSimulations),
    });
  };

  const inputClass =
    "w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary focus:border-primary focus:outline-none";
  const labelClass = "mb-1 block text-sm text-text-secondary";

  return (
    <form onSubmit={handleSubmit} aria-label="Simulation parameters" noValidate>
      <div className="space-y-4">
        <div>
          <label htmlFor="odds" className={labelClass}>
            Odds (American)
          </label>
          <input
            id="odds"
            type="number"
            value={state.oddsAmerican}
            onChange={(e) => set("oddsAmerican")(e.target.value)}
            className={inputClass}
          />
          {impliedProb !== null && (
            <p data-testid="implied-prob" className="mt-1 text-xs text-text-muted">
              Implied probability: {(impliedProb * 100).toFixed(2)}%
            </p>
          )}
          {errors.odds && <p role="alert" className="mt-1 text-xs text-danger">{errors.odds}</p>}
        </div>

        <div>
          <label htmlFor="win-probability" className={labelClass}>
            Win probability (%)
          </label>
          <input
            id="win-probability"
            type="number"
            value={state.winProbabilityPct}
            onChange={(e) => set("winProbabilityPct")(e.target.value)}
            className={inputClass}
          />
          {errors.winProbability && (
            <p role="alert" className="mt-1 text-xs text-danger">{errors.winProbability}</p>
          )}
        </div>

        <div>
          <label htmlFor="bankroll" className={labelClass}>
            Bankroll ($)
          </label>
          <input
            id="bankroll"
            type="number"
            value={state.bankroll}
            onChange={(e) => set("bankroll")(e.target.value)}
            className={inputClass}
          />
          {errors.bankroll && <p role="alert" className="mt-1 text-xs text-danger">{errors.bankroll}</p>}
        </div>

        <div>
          <label htmlFor="bet-size-type" className={labelClass}>
            Bet strategy
          </label>
          <select
            id="bet-size-type"
            value={state.betSizeType}
            onChange={(e) => set("betSizeType")(e.target.value)}
            className={inputClass}
          >
            {BET_SIZE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="bet-size" className={labelClass}>
            Bet size ($ or fraction)
          </label>
          <input
            id="bet-size"
            type="number"
            value={state.betSize}
            onChange={(e) => set("betSize")(e.target.value)}
            className={inputClass}
          />
          {errors.betSize && <p role="alert" className="mt-1 text-xs text-danger">{errors.betSize}</p>}
        </div>

        <div>
          <label htmlFor="num-bets" className={labelClass}>
            Bets per simulation
          </label>
          <input
            id="num-bets"
            type="number"
            value={state.numBets}
            onChange={(e) => set("numBets")(e.target.value)}
            className={inputClass}
          />
          {errors.numBets && <p role="alert" className="mt-1 text-xs text-danger">{errors.numBets}</p>}
        </div>

        <div>
          <label htmlFor="num-simulations" className={labelClass}>
            Number of simulations
          </label>
          <input
            id="num-simulations"
            type="number"
            value={state.numSimulations}
            onChange={(e) => set("numSimulations")(e.target.value)}
            className={inputClass}
          />
          {errors.numSimulations && (
            <p role="alert" className="mt-1 text-xs text-danger">{errors.numSimulations}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={false}
          className="w-full rounded-md bg-primary px-4 py-2.5 font-semibold text-bg-primary hover:bg-primary-hover"
        >
          Run Simulation
        </button>
      </div>
    </form>
  );
}
