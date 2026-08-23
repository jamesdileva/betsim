import { useState } from "react";
import ExplainabilityPanel from "../components/ExplainabilityPanel";
import SystemPlaysResults from "../components/SystemPlaysResults";
import { calibrate } from "../services/systemPlaysApi";
import { predict } from "../services/mlApi";
import { americanToImpliedProb, type BetSizeType } from "../types/simulation";
import type { CalibrationReport } from "../types/systemPlays";
import type { ModelPrediction } from "../types/ml";

const inputClass =
  "w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary focus:border-primary focus:outline-none";
const labelClass = "mb-1 block text-sm text-text-secondary";

export default function SystemPlays() {
  const [form, setForm] = useState({
    oddsAmerican: "-110",
    modelProbabilityPct: "60",
    bankroll: "1000",
    betSize: "100",
    betSizeType: "flat",
    numBets: "100",
    numSimulations: "5000",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<CalibrationReport | null>(null);
  const [modelSource, setModelSource] = useState<"user_input" | "stub">("user_input");
  const [prediction, setPrediction] = useState<ModelPrediction | null>(null);

  const set = (key: keyof typeof form) => (value: string) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const impliedProb = (() => {
    const odds = Number(form.oddsAmerican);
    if (Number.isNaN(odds) || odds === 0 || Math.abs(odds) < 100) return null;
    return americanToImpliedProb(odds);
  })();

  const handleCalibrate = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setReport(null);
    setPrediction(null);
    const winProbability = Number(form.modelProbabilityPct) / 100;
    const oddsAmerican = Number(form.oddsAmerican);
    try {
      const [calibration, modelPrediction] = await Promise.all([
        calibrate({
          odds_american: oddsAmerican,
          win_probability: winProbability,
          bankroll: Number(form.bankroll),
          bet_size: Number(form.betSize),
          bet_size_type: form.betSizeType as BetSizeType,
          num_bets: Number(form.numBets),
          num_simulations: Number(form.numSimulations),
          seed: 42,
        }),
        predict({
          source: modelSource,
          win_probability:
            modelSource === "user_input" ? winProbability : undefined,
          odds_american: oddsAmerican,
        }),
      ]);
      setReport(calibration);
      setPrediction(modelPrediction);
    } catch (err: unknown) {
      setError(
        err instanceof Error
          ? `Calibration failed. ${err.message}`
          : "Calibration failed.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 gap-8 p-6 lg:grid-cols-[360px_1fr]">
      <div className="rounded-lg border border-border bg-bg-secondary p-5">
        <h1 className="mb-1 text-lg font-bold">System Plays Engine</h1>
        <p className="mb-4 text-xs text-text-muted">
          Is your probability estimate actually correct? Simulate it and find out.
        </p>
        <form onSubmit={handleCalibrate} aria-label="System Plays calibration" noValidate>
          <div className="space-y-4">
            <div>
              <label htmlFor="sp-odds" className={labelClass}>Odds (American)</label>
              <input id="sp-odds" type="number" value={form.oddsAmerican} onChange={(e) => set("oddsAmerican")(e.target.value)} className={inputClass} />
              {impliedProb !== null && (
                <p className="mt-1 text-xs text-text-muted">Bookmaker implied: {(impliedProb * 100).toFixed(2)}%</p>
              )}
            </div>
            <div>
              <label htmlFor="sp-prob" className={labelClass}>Model probability (%)</label>
              <input id="sp-prob" type="number" value={form.modelProbabilityPct} onChange={(e) => set("modelProbabilityPct")(e.target.value)} className={inputClass} />
            </div>
            <div>
              <span className={labelClass}>Probability source</span>
              <div data-testid="model-source-selector" className="flex gap-4 text-sm text-text-secondary">
                <label className="flex items-center gap-1.5">
                  <input
                    type="radio"
                    name="model-source"
                    checked={modelSource === "user_input"}
                    onChange={() => setModelSource("user_input")}
                  />
                  User input
                </label>
                <label className="flex items-center gap-1.5">
                  <input
                    type="radio"
                    name="model-source"
                    checked={modelSource === "stub"}
                    onChange={() => setModelSource("stub")}
                  />
                  Stub model
                </label>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label htmlFor="sp-bankroll" className={labelClass}>Bankroll ($)</label>
                <input id="sp-bankroll" type="number" value={form.bankroll} onChange={(e) => set("bankroll")(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label htmlFor="sp-bets" className={labelClass}>Bets</label>
                <input id="sp-bets" type="number" value={form.numBets} onChange={(e) => set("numBets")(e.target.value)} className={inputClass} />
              </div>
              <div>
                <label htmlFor="sp-size-type" className={labelClass}>Bet strategy</label>
                <select id="sp-size-type" value={form.betSizeType} onChange={(e) => set("betSizeType")(e.target.value)} className={inputClass}>
                  <option value="flat">Flat $</option>
                  <option value="percentage">% of bankroll</option>
                  <option value="kelly">Kelly</option>
                  <option value="half_kelly">Half Kelly</option>
                </select>
              </div>
              <div>
                <label htmlFor="sp-bet-size" className={labelClass}>Bet size ($ / frac)</label>
                <input id="sp-bet-size" type="number" value={form.betSize} onChange={(e) => set("betSize")(e.target.value)} className={inputClass} />
              </div>
            </div>
            <div>
              <label htmlFor="sp-sims" className={labelClass}>Simulations (100–100,000)</label>
              <input id="sp-sims" type="number" value={form.numSimulations} onChange={(e) => set("numSimulations")(e.target.value)} className={inputClass} />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-md bg-primary px-4 py-2.5 font-semibold text-bg-primary hover:bg-primary-hover disabled:opacity-50"
            >
              {loading ? "Calibrating..." : "Calibrate Model"}
            </button>
          </div>
        </form>
      </div>

      <div>
        <h2 className="mb-4 text-lg font-bold">Calibration report</h2>
        {loading && (
          <div role="status" data-testid="calibration-loading" className="py-12">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-bg-tertiary border-t-primary" />
            <p className="mt-3 text-center text-text-muted">Running simulations...</p>
          </div>
        )}
        {!loading && error && (
          <div role="alert" data-testid="calibration-error" className="rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
            {error}
          </div>
        )}
        {!loading && !report && !error && (
          <p className="text-text-muted" data-testid="calibration-placeholder">
            Enter your probability estimate and run the engine to see how calibrated you are.
          </p>
        )}
        {!loading && report && (
          <div className="space-y-6">
            <SystemPlaysResults report={report} />
            {prediction && (
              <ExplainabilityPanel
                factors={prediction.top_factors}
                confidence={prediction.confidence}
              />
            )}
          </div>
        )}
      </div>
    </div>
  );
}
