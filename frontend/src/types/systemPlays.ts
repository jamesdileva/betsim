export type CalibrationStatus = "well_calibrated" | "overconfident" | "underconfident";

export interface CalibrationReport {
  stated_probability: number;
  actual_win_rate: number;
  calibration_error: number;
  calibration_status: CalibrationStatus | string;
  confidence_interval_low: number;
  confidence_interval_high: number;
  recommendation: string;
}

export interface CalibrationRequest {
  odds_american: number;
  win_probability: number;
  bankroll: number;
  bet_size: number;
  bet_size_type: string;
  num_bets: number;
  num_simulations: number;
  seed?: number | null;
}

export const STATUS_LABELS: Record<string, string> = {
  well_calibrated: "Well Calibrated",
  overconfident: "Overconfident",
  underconfident: "Underconfident",
};

export function statusColorClass(status: string): string {
  if (status === "well_calibrated") return "text-success";
  if (status === "underconfident") return "text-warning";
  return "text-danger";
}
