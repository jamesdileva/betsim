import CalibrationChart from "./CalibrationChart";
import {
  STATUS_LABELS,
  statusColorClass,
  type CalibrationReport,
} from "../types/systemPlays";

function pct(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

interface SystemPlaysResultsProps {
  report: CalibrationReport;
}

export default function SystemPlaysResults({ report }: SystemPlaysResultsProps) {
  return (
    <div data-testid="system-plays-results" className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <div className="rounded-lg border border-border bg-bg-secondary p-4">
          <p className="text-xs uppercase tracking-wide text-text-muted">Stated probability</p>
          <p data-testid="report-stated" className="mt-1 text-2xl font-bold">
            {pct(report.stated_probability)}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-bg-secondary p-4">
          <p className="text-xs uppercase tracking-wide text-text-muted">Actual win rate</p>
          <p data-testid="report-actual" className="mt-1 text-2xl font-bold">
            {pct(report.actual_win_rate)}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-bg-secondary p-4">
          <p className="text-xs uppercase tracking-wide text-text-muted">Calibration error</p>
          <p data-testid="report-error" className="mt-1 text-2xl font-bold">
            {pct(report.calibration_error)}
          </p>
        </div>
        <div className="rounded-lg border border-border bg-bg-secondary p-4">
          <p className="text-xs uppercase tracking-wide text-text-muted">Status</p>
          <p
            data-testid="report-status"
            className={`mt-1 text-2xl font-bold ${statusColorClass(report.calibration_status)}`}
          >
            {STATUS_LABELS[report.calibration_status] ?? report.calibration_status}
          </p>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-bg-secondary p-4">
        <h3 className="mb-1 text-sm font-semibold uppercase tracking-wide text-text-muted">
          95% confidence interval (actual win rate)
        </h3>
        <p data-testid="report-ci" className="text-text-primary">
          [{pct(report.confidence_interval_low)} — {pct(report.confidence_interval_high)}]
        </p>
        <p className="mt-3 text-sm text-text-secondary" data-testid="report-recommendation">
          {report.recommendation}
        </p>
      </div>

      <CalibrationChart report={report} />
    </div>
  );
}
