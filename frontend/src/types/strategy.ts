export interface Strategy {
  id: number;
  name: string;
  odds_american: number | null;
  win_probability: number | null;
  bankroll: number | null;
  bet_size: number | null;
  bet_size_type: string | null;
  num_bets: number | null;
  num_simulations: number | null;
  strategy_type: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface StrategyCreateInput {
  name: string;
  odds_american: number;
  win_probability: number;
  bankroll: number;
  bet_size: number;
  bet_size_type: string;
  num_bets: number;
  num_simulations: number;
}

export interface RunSummary {
  run_id: number;
  strategy_id: number | null;
  odds_american: number | null;
  win_probability: number | null;
  bankroll: number | null;
  bet_size: number | null;
  bet_size_type: string | null;
  num_bets: number | null;
  num_simulations: number | null;
  created_at: string | null;
  result_count: number;
  win_pct: number | null;
  avg_final_bankroll: number | null;
  risk_of_ruin: number | null;
}
