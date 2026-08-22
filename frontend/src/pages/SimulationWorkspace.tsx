import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import ExportButton from "../components/ExportButton";
import OddsSelector from "../components/OddsSelector";
import SimulationForm, { type FormValues } from "../components/SimulationForm";
import SimulationResults from "../components/SimulationResults";
import ScenarioLibrary from "../components/ScenarioLibrary";
import StrategyComparison from "../components/StrategyComparison";
import type { Scenario } from "../data/scenarios";
import { useSimulation } from "../hooks/useSimulation";
import { createStrategy } from "../services/strategiesApi";
import { loadSettings } from "../services/settings";
import type { SimulationParams } from "../types/simulation";

export default function SimulationWorkspace() {
  const { status, result, error, runSimulation } = useSimulation();
  const settings = loadSettings();
  const location = useLocation();
  const [scenarioValues, setScenarioValues] = useState<FormValues | null>(null);
  const [lastParams, setLastParams] = useState<SimulationParams | null>(null);
  const [saveName, setSaveName] = useState("");
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved" | "error">("idle");

  // Re-run support: Strategies page and History page navigate here with params.
  const rerunParams = (location.state as { rerunParams?: SimulationParams } | null)?.rerunParams;
  useEffect(() => {
    if (!rerunParams) return;
    setScenarioValues({
      oddsAmerican: rerunParams.odds_american,
      winProbabilityPct: rerunParams.win_probability * 100,
      bankroll: rerunParams.bankroll,
      betSize: rerunParams.bet_size,
      betSizeType: rerunParams.bet_size_type,
      numBets: rerunParams.num_bets,
      numSimulations: rerunParams.num_simulations,
    });
    void runSimulation(rerunParams);
    window.history.replaceState({}, "");
  }, [rerunParams, runSimulation]);

  const handleApplyScenario = (scenario: Scenario) => {
    setScenarioValues({
      oddsAmerican: scenario.params.odds_american,
      winProbabilityPct: scenario.params.win_probability * 100,
      bankroll: scenario.params.bankroll,
      betSize: scenario.params.bet_size,
      betSizeType: scenario.params.bet_size_type,
      numBets: scenario.params.num_bets,
      numSimulations: scenario.params.num_simulations,
    });
  };

  const handleSaveStrategy = async () => {
    if (!lastParams || !saveName.trim()) return;
    setSaveState("saving");
    try {
      await createStrategy({ name: saveName.trim(), ...lastParams });
      setSaveState("saved");
      setShowSaveDialog(false);
      setSaveName("");
    } catch {
      setSaveState("error");
    }
  };

  const wrappedRun = (params: SimulationParams) => {
    setLastParams(params);
    void runSimulation(params);
  };

  return (
    <div className="grid grid-cols-1 gap-8 p-6 lg:grid-cols-[360px_1fr]">
      <div className="space-y-4">
        <div className="rounded-lg border border-border bg-bg-secondary p-5">
          <h1 className="mb-4 text-lg font-bold">Bet parameters</h1>
          <SimulationForm
            defaults={{
              bankroll: settings.defaultBankroll,
              num_bets: settings.defaultBets,
              num_simulations: settings.defaultSimulations,
            }}
            initialValues={scenarioValues}
            onRun={wrappedRun}
          />
        </div>
        <div className="rounded-lg border border-border bg-bg-secondary p-5">
          <ScenarioLibrary onApply={handleApplyScenario} />
        </div>
        <div className="rounded-lg border border-border bg-bg-secondary p-5">
          <OddsSelector
            onApply={(oddsAmerican) =>
              setScenarioValues((prev) => ({ ...(prev ?? {}), oddsAmerican }))
            }
          />
        </div>
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-lg font-bold">Simulation results</h1>
          <div className="flex items-center gap-2" data-testid="workspace-actions">
            <button
              type="button"
              data-testid="save-strategy-button"
              disabled={!result}
              onClick={() => {
                setShowSaveDialog(true);
                setSaveState("idle");
              }}
              className={`rounded-md px-3 py-1.5 text-sm font-semibold ${
                result
                  ? "bg-primary text-bg-primary hover:bg-primary-hover"
                  : "cursor-not-allowed bg-bg-tertiary text-text-muted"
              }`}
            >
              Save Strategy
            </button>
            <ExportButton result={result} />
          </div>
        </div>

        {status === "error" ? (
          <div
            role="alert"
            data-testid="results-error"
            className="rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger"
          >
            {error}
          </div>
        ) : (
          <>
            <SimulationResults result={result} isRunning={status === "loading"} />
            {result && <StrategyComparison params={lastParams} />}
          </>
        )}
      </div>

      {showSaveDialog && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label="Save strategy"
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/70 p-4"
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void handleSaveStrategy();
            }}
            className="w-full max-w-sm rounded-lg border border-border bg-bg-secondary p-5"
          >
            <h2 className="mb-3 text-lg font-bold">Save strategy</h2>
            <label htmlFor="strategy-name" className="mb-1 block text-xs text-text-secondary">
              Strategy name
            </label>
            <input
              id="strategy-name"
              value={saveName}
              onChange={(e) => setSaveName(e.target.value)}
              placeholder="NFL Week 1 -5"
              required
              autoFocus
              className="w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary focus:border-primary focus:outline-none"
            />
            {saveState === "error" && (
              <p role="alert" className="mt-2 text-sm text-danger">
                Could not save the strategy. Is the backend running?
              </p>
            )}
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowSaveDialog(false)}
                className="rounded-md border border-border px-4 py-2 text-sm text-text-secondary hover:text-text-primary"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saveState === "saving"}
                className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-bg-primary hover:bg-primary-hover disabled:opacity-50"
              >
                {saveState === "saving" ? "Saving..." : "Save"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
