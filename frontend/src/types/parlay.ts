export interface ParlayLegInput {
  oddsAmerican: string;
  winProbabilityPct: string;
}

export const DEFAULT_LEG: ParlayLegInput = { oddsAmerican: "-110", winProbabilityPct: "55" };
