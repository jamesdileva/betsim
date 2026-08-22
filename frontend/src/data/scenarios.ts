import type { SimulationParams } from "../types/simulation";

export interface Scenario {
  id: string;
  name: string;
  description: string;
  params: SimulationParams;
}

/**
 * Pre-built betting scenarios (Product Design, Workflow 7).
 * Each is instantly loadable into the workspace form.
 */
export const SCENARIOS: Scenario[] = [
  {
    id: "nfl-favorite",
    name: "NFL Favorite -3 @ -110",
    description: "Heavy favorite, moderate edge, standard bankroll.",
    params: {
      odds_american: -110,
      win_probability: 0.65,
      bankroll: 1000,
      bet_size: 50,
      bet_size_type: "flat",
      num_bets: 100,
      num_simulations: 5000,
    },
  },
  {
    id: "mma-underdog",
    name: "MMA Underdog +200",
    description: "Longshot with a thin edge — high variance.",
    params: {
      odds_american: 200,
      win_probability: 0.35,
      bankroll: 500,
      bet_size: 25,
      bet_size_type: "flat",
      num_bets: 50,
      num_simulations: 5000,
    },
  },
  {
    id: "high-edge-value",
    name: "High-edge Value Play +150",
    description: "Coin-flip estimate at plus money: strong edge on paper.",
    params: {
      odds_american: 150,
      win_probability: 0.5,
      bankroll: 1000,
      bet_size: 100,
      bet_size_type: "flat",
      num_bets: 100,
      num_simulations: 5000,
    },
  },
  {
    id: "kelly-grinder",
    name: "Kelly Grinder -105",
    description: "Small edge, Kelly-sized bets — the long-term compounding play.",
    params: {
      odds_american: -105,
      win_probability: 0.53,
      bankroll: 2000,
      bet_size: 100,
      bet_size_type: "kelly",
      num_bets: 250,
      num_simulations: 5000,
    },
  },
];
