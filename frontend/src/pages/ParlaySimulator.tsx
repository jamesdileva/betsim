import { useMemo, useState } from "react";
import type { ParlayResultsProps } from "../components/ParlayResults";
import BankrollStrategySelector from "../components/BankrollStrategySelector";
import { DEFAULT_LEG, type ParlayLegInput } from "../types/parlay";
import ParlayBuilder from "../components/ParlayBuilder";
import ParlayResults from "../components/ParlayResults";
import { simulateParlay } from "../services/parlayApi";
import type { BetSizeType } from "../types/simulation";

const inputClass =
  "w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary focus:border-primary focus:outline-none";
const labelClass = "mb-1 block text-sm text-text-secondary";

interface ParlayResponseState {
  combinedProbability: number;
  combinedDecimalOdds: number;
  evPerUnit: number;
  breakEvenProbability: number;
  metrics: ParlayResultsProps["metrics"];
  distribution: ParlayResultsProps["distribution"];
}

export default function ParlaySimulator() {
  const [legs, setLegs] = useState<ParlayLegInput[]>([{ ...DEFAULT_LEG }, { ...DEFAULT_LEG }]);
  const [bankroll, setBankroll] = useState("1000");
  const [betSize, setBetSize] = useState("100");
  const [betSizeType, setBetSizeType] = useState<BetSizeType>("flat");
  const [numBets, setNumBets] = useState("1");
  const [numSimulations, setNumSimulations] = useState("5000");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ParlayResponseState | null>(null);

  const allLegsValid = legs.every(
    (leg) =>
      Number(leg.oddsAmerican) !== 0 &&
      Math.abs(Number(leg.oddsAmerican)) >= 100 &&
      Number(leg.winProbabilityPct) > 0 &&
      Number(leg.winProbabilityPct) < 100,
  );

  // live combined math (client-side preview before running the simulation)
  const preview = useMemo(() => {
    if (!allLegsValid) return null;
    let prob = 1;
    let decimal = 1;
    for (const leg of legs) {
      prob *= Number(leg.winProbabilityPct) / 100;
      const o = Number(leg.oddsAmerican);
      decimal *= o > 0 ? 1 + o / 100 : 1 + 100 / Math.abs(o);
    }
    return {
      probability: prob,
      decimalOdds: decimal,
      evPerUnit: prob * (decimal - 1) - (1 - prob),
      breakEven: 1 / decimal,
    };
  }, [legs, allLegsValid]);

  const handleRun = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!allLegsValid) return;
    setLoading(true);
    setError(null);
    try {
      const response = await simulateParlay({
        legs: legs.map((leg) => ({
          odds_american: Number(leg.oddsAmerican),
          win_probability: Number(leg.winProbabilityPct) / 100,
        })),
        bankroll: Number(bankroll),
        bet_size: Number(betSize),
        bet_size_type: betSizeType,
        num_bets: Number(numBets),
        num_simulations: Number(numSimulations),
        seed: 42,
      });
      setResult({
        combinedProbability: response.combined_probability,
        combinedDecimalOdds: response.combined_decimal_odds,
        evPerUnit: response.ev_per_unit,
        breakEvenProbability: response.break_even_probability,
        metrics: response.metrics,
        distribution: response.distribution,
      });
    } catch (err: unknown) {
      setError(err instanceof Error ? `Parlay simulation failed. ${err.message}` : "Failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-8 p-6 lg:grid-cols-[420px_1fr]">
      <div className="rounded-lg border border-border bg-bg-secondary p-5">
        <h1 className="mb-1 text-lg font-bold">Parlay Simulator</h1>
        <p className="mb-4 text-xs text-text-muted">
          All legs must win. Watch how variance explodes.
        </p>
        <form onSubmit={handleRun} aria-label="Parlay simulation" noValidate>
          <div className="space-y-4">
            <ParlayBuilder legs={legs} onChange={setLegs} />

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="parlay-bankroll" className={labelClass}>Bankroll ($)</label>
                <input id="parlay-bankroll" type="number" value={bankroll} onChange={(e) => setBankroll(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label htmlFor="parlay-size" className={labelClass}>Bet size ($ / frac)</label>
                <input id="parlay-size" type="number" value={betSize} onChange={(e) => setBetSize(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label htmlFor="parlay-bets" className={labelClass}>Parlays per run</label>
                <input id="parlay-bets" type="number" value={numBets} onChange={(e) => setNumBets(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label htmlFor="parlay-sims" className={labelClass}>Simulations</label>
                <input id="parlay-sims" type="number" value={numSimulations} onChange={(e) => setNumSimulations(e.target.value)} className={inputClass} />
              </div>
            </div>

            <BankrollStrategySelector value={betSizeType} onChange={setBetSizeType} />

            {preview && (
              <div data-testid="parlay-preview" className="rounded-md border border-border bg-bg-tertiary p-3 text-sm text-text-secondary">
                Combined: {(preview.probability * 100).toFixed(1)}% @{" "}
                {preview.decimalOdds.toFixed(2)}x · EV per unit{" "}
                <span className={preview.evPerUnit >= 0 ? "text-success" : "text-danger"}>
                  {(preview.evPerUnit * 100).toFixed(1)}%
                </span>{" "}
                · break-even {(preview.breakEven * 100).toFixed(1)}%
              </div>
            )}

            <button
              type="submit"
              disabled={!allLegsValid || loading}
              className="w-full rounded-md bg-primary px-4 py-2.5 font-semibold text-bg-primary hover:bg-primary-hover disabled:opacity-50"
            >
              {loading ? "Running..." : "Run Parlay Simulation"}
            </button>
          </div>
        </form>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-bold">Parlay analytics</h2>
        {loading && (
          <div role="status" data-testid="parlay-loading" className="py-12">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-bg-tertiary border-t-primary" />
            <p className="mt-3 text-center text-text-muted">Simulating parlays...</p>
          </div>
        )}
        {!loading && error && (
          <div role="alert" data-testid="parlay-error" className="rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
            {error}
          </div>
        )}
        {!loading && !result && !error && (
          <p className="text-text-muted" data-testid="parlay-placeholder">
            Build a parlay and run the simulation to see true risk vs. single bets.
          </p>
        )}
        {!loading && result && <ParlayResults {...result} />}
      </div>
    </div>
  );
}

