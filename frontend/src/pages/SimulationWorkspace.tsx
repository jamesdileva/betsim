import ResultsDisplay from "../components/ResultsDisplay";
import SimulationForm from "../components/SimulationForm";
import { useSimulation } from "../hooks/useSimulation";
import { loadSettings } from "../services/settings";

export default function SimulationWorkspace() {
  const { status, result, error, runSimulation } = useSimulation();
  const settings = loadSettings();

  return (
    <div className="grid grid-cols-1 gap-8 p-6 lg:grid-cols-[360px_1fr]">
      <div className="rounded-lg border border-border bg-bg-secondary p-5">
        <h1 className="mb-4 text-lg font-bold">Bet parameters</h1>
        <SimulationForm
          defaults={{
            bankroll: settings.defaultBankroll,
            num_bets: settings.defaultBets,
            num_simulations: settings.defaultSimulations,
          }}
          onRun={runSimulation}
        />
      </div>

      <div>
        <h1 className="mb-4 text-lg font-bold">Simulation results</h1>
        {status === "idle" && (
          <p className="text-text-muted" data-testid="results-placeholder">
            Fill in your bet parameters and run a simulation to see results.
          </p>
        )}
        {status === "loading" && (
          <div role="status" aria-live="polite" data-testid="loading-spinner" className="py-12">
            <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-bg-tertiary border-t-primary" />
            <p className="mt-3 text-center text-text-muted">Running simulations...</p>
          </div>
        )}
        {status === "error" && (
          <div role="alert" data-testid="results-error" className="rounded-lg border border-danger/50 bg-danger/10 p-4 text-danger">
            {error}
          </div>
        )}
        {status === "success" && result && <ResultsDisplay metrics={result.metrics} />}
      </div>
    </div>
  );
}
