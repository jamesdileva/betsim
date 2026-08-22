export interface MetricSummary {
  win_pct: number;
  avg_ending_bankroll: number;
  median_ending_bankroll: number;
  std_dev: number;
  min_bankroll: number;
  max_bankroll: number;
  risk_of_ruin: number;
  avg_max_drawdown: number;
  worst_case_drawdown: number;
  ev_per_bet: number;
  ev_total: number;
}

export interface DistributionData {
  bin_edges: number[];
  counts: number[];
}

export interface TrajectoryBands {
  p10: number[];
  median: number[];
  p90: number[];
  min: number[];
  max: number[];
}

export type BetSizeType = "flat" | "percentage" | "kelly" | "half_kelly";

export interface SimulationParams {
  odds_american: number;
  win_probability: number;
  bankroll: number;
  bet_size: number;
  bet_size_type: BetSizeType;
  num_bets: number;
  num_simulations: number;
  seed?: number | null;
}

export interface SimulationResult {
  run_id: number;
  metrics: MetricSummary;
  distribution: DistributionData;
  trajectory: TrajectoryBands;
}

export function americanToImpliedProb(oddsAmerican: number): number {
  if (oddsAmerican > 0) return 100 / (oddsAmerican + 100);
  return Math.abs(oddsAmerican) / (Math.abs(oddsAmerican) + 100);
}
