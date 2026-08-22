import type { SimulationResult } from "../types/simulation";
import BankrollChart from "./BankrollChart";
import DistributionChart from "./DistributionChart";
import MetricsTable from "./MetricsTable";
import ResultsDisplay from "./ResultsDisplay";

interface SimulationResultsProps {
  result: SimulationResult | null;
  isRunning?: boolean;
}

export default function SimulationResults({ result, isRunning = false }: SimulationResultsProps) {
  if (isRunning) {
    return (
      <div role="status" aria-live="polite" data-testid="loading-spinner" className="py-12">
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-bg-tertiary border-t-primary" />
        <p className="mt-3 text-center text-text-muted">Running simulations...</p>
      </div>
    );
  }

  if (!result) {
    return (
      <p className="text-text-muted" data-testid="results-placeholder">
        Fill in your bet parameters and run a simulation to see results.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <ResultsDisplay metrics={result.metrics} />
      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
        <BankrollChart bands={result.trajectory} />
        <DistributionChart distribution={result.distribution} />
      </div>
      <MetricsTable metrics={result.metrics} />
    </div>
  );
}
