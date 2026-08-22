import type { DistributionData, MetricSummary } from "../types/simulation";

export interface ParlayResponse {
  combined_probability: number;
  combined_decimal_odds: number;
  ev_per_unit: number;
  break_even_probability: number;
  run_id: number;
  metrics: MetricSummary;
  distribution: DistributionData;
}
