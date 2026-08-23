export interface Factor {
  feature: string;
  label: string;
  impact: number;
  direction: "+" | "-";
}

export interface ModelPrediction {
  probability: number;
  confidence: number;
  fair_odds_decimal: number;
  ev_vs_market: number | null;
  top_factors: Factor[];
  features_used: number;
}
