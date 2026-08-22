import { americanToImpliedProb } from "../types/simulation";

/**
 * Kelly fraction for American odds + win probability, clamped to [0, 1] with
 * 0 on no-edge — mirrors backend simulation.kelly.kelly_criterion.
 */
export function kellyFraction(oddsAmerican: number, winProbability: number): number {
  const decimal =
    oddsAmerican > 0 ? 1 + oddsAmerican / 100 : 1 + 100 / Math.abs(oddsAmerican);
  const b = decimal - 1;
  if (b <= 0 || winProbability <= 0 || winProbability >= 1) return 0;
  return Math.max(0, Math.min(1, (b * winProbability - (1 - winProbability)) / b));
}

export { americanToImpliedProb };
