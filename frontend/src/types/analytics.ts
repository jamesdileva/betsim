export interface ModelEvaluationRow {
  id: number;
  evaluated_at: string | null;
  accuracy: number | null;
  calibration_error: number | null;
  avg_roi: number | null;
  brier_score: number | null;
  notes: string | null;
}

export interface ModelPerformanceSummary {
  model_id: string;
  backtest_count: number;
  accuracy: number | null;
  avg_roi: number | null;
}

export interface PerformanceResponse {
  summary: ModelPerformanceSummary[];
  evaluations: Record<string, ModelEvaluationRow[]>;
}

export interface RunBacktestsResponse {
  backtests_created: number;
}
