export interface LiveOddsRow {
  sportsbook: string | null;
  outcome_name: string | null;
  market_type: string | null;
  odds_american: number | null;
  odds_decimal: number | null;
  implied_probability: number | null;
  timestamp: string | null;
}

export interface LiveGame {
  game_id: string;
  sport: string;
  home_team: string | null;
  away_team: string | null;
  game_time: string | null;
  status: string | null;
  stale: boolean;
  fetched_at: string | null;
  odds: LiveOddsRow[];
}

export interface GamesResponse {
  sport: string;
  stale: boolean;
  games: LiveGame[];
}

export const SPORT_OPTIONS = [
  { value: "americanfootball_nfl", label: "NFL" },
  { value: "basketball_nba", label: "NBA" },
  { value: "baseball_mlb", label: "MLB" },
  { value: "icehockey_nhl", label: "NHL" },
];

/** Best (highest) American price per side from the latest snapshots. */
export function bestPricesForSides(game: LiveGame): { home: number | null; away: number | null } {
  const timestamps = game.odds.map((r) => r.timestamp).filter((t): t is string => !!t);
  const latestTs = timestamps.length ? timestamps.reduce((a, b) => (a > b ? a : b)) : null;
  const latest = game.odds.filter((r) => r.timestamp === latestTs);
  const pick = (side: string | null) => {
    const rows = latest.filter((r) => r.outcome_name === side && r.odds_american !== null);
    return rows.length ? Math.max(...rows.map((r) => r.odds_american as number)) : null;
  };
  return { home: pick(game.home_team), away: pick(game.away_team) };
}
