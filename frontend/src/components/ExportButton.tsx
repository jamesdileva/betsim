import type { SimulationResult } from "../types/simulation";
import { downloadCsv, resultToCsv } from "../utils/csvExport";

interface ExportButtonProps {
  result: SimulationResult | null;
}

export default function ExportButton({ result }: ExportButtonProps) {
  const disabled = !result;
  return (
    <button
      type="button"
      disabled={disabled}
      data-testid="export-csv"
      onClick={() => {
        if (!result) return;
        downloadCsv(`betsim-run-${result.run_id}.csv`, resultToCsv(result));
      }}
      className={`rounded-md border border-border px-3 py-1.5 text-sm ${
        disabled ? "cursor-not-allowed text-text-muted" : "text-text-secondary hover:text-text-primary"
      }`}
      title={disabled ? "Run a simulation first" : "Download results as CSV"}
    >
      Export CSV
    </button>
  );
}
