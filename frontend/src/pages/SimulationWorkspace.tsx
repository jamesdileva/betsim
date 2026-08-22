import { useState } from "react";
import ScenarioLibrary from "../components/ScenarioLibrary";
import SimulationForm, { type FormValues } from "../components/SimulationForm";
import SimulationResults from "../components/SimulationResults";
import type { Scenario } from "../data/scenarios";
import { useSimulation } from "../hooks/useSimulation";
import { loadSettings } from "../services/settings";

export default function SimulationWorkspace() {
  const { status, result, error, runSimulation } = useSimulation();
  const settings = loadSettings();
  const [scenarioValues, setScenarioValues] = useState<FormValues | null>(null);

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
            onRun={runSimulation}
          />
        </div>
        <div className="rounded-lg border border-border bg-bg-secondary p-5">
          <ScenarioLibrary onApply={handleApplyScenario} />
        </div>
      </div>

      <div>
        <h1 className="mb-4 text-lg font-bold">Simulation results</h1>
        {status === "error" ? (
          <div
            role="alert"
            data-testid="results-error"
            className="rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger"
          >
            {error}
          </div>
        ) : (
          <SimulationResults result={result} isRunning={status === "loading"} />
        )}
      </div>
    </div>
  );
}
