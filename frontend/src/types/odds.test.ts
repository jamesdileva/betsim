import { describe, expect, it } from "vitest";
import { bestPricesForSides, type LiveGame } from "./odds";

const GAME: LiveGame = {
  game_id: "g1",
  sport: "americanfootball_nfl",
  home_team: "Chiefs",
  away_team: "Bills",
  game_time: "2026-09-10T17:15:00Z",
  status: "scheduled",
  stale: false,
  fetched_at: "2026-08-22T12:00:00Z",
  odds: [
    {
      sportsbook: "draftkings",
      outcome_name: "Chiefs",
      market_type: "moneyline",
      odds_american: -150,
      odds_decimal: 1.67,
      implied_probability: 0.6,
      timestamp: "2026-08-22T12:00:00",
    },
    {
      sportsbook: "fanduel",
      outcome_name: "Chiefs",
      market_type: "moneyline",
      odds_american: -140,
      odds_decimal: 1.71,
      implied_probability: 0.583,
      timestamp: "2026-08-22T11:30:00",
    },
    {
      sportsbook: "draftkings",
      outcome_name: "Bills",
      market_type: "moneyline",
      odds_american: 130,
      odds_decimal: 2.3,
      implied_probability: 0.435,
      timestamp: "2026-08-22T12:00:00",
    },
  ],
};

describe("bestPricesForSides", () => {
  it("uses only the latest snapshot and returns best price per side", () => {
    const prices = bestPricesForSides(GAME);
    // fanduel's -140 is from an OLDER timestamp (11:30); latest is 12:00
    expect(prices.home).toBe(-150);
    expect(prices.away).toBe(130);
  });

  it("handles games with missing sides", () => {
    const empty: LiveGame = { ...GAME, odds: [] };
    expect(bestPricesForSides(empty)).toEqual({ home: null, away: null });
  });
});
