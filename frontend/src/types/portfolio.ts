export interface ScoreBreakdownEntry {
  value: number | string;
  points: number;
  max: number;
  applied?: string;
}

export interface IntelligenceScoreData {
  score: number;
  stars: number;
  risk_level: string;
  breakdown: Record<string, ScoreBreakdownEntry>;
}

export interface PortfolioItemData {
  id: number;
  portfolio_id?: number;
  game_id: string | null;
  model_id: string | null;
  confidence_level: string | null;
  bet_type: string | null;
  stake: number | null;
  predicted_probability: number | null;
  ev: number | null;
  recommendation_stars: number | null;
}

export interface Portfolio {
  id: number;
  date: string | null;
  total_risk: number | null;
  expected_roi: number | null;
  kelly_exposure: number | null;
  model_id: string | null;
  items: PortfolioItemData[];
}
