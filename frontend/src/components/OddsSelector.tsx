import { useEffect, useState } from "react";
import LiveOddsBadge from "./LiveOddsBadge";
import { listGames } from "../services/oddsApi";
import {
  SPORT_OPTIONS,
  bestPricesForSides,
  type GamesResponse,
  type LiveGame,
} from "../types/odds";

interface OddsSelectorProps {
  onApply: (oddsAmerican: number, game: LiveGame) => void;
}

const inputClass =
  "w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-sm text-text-primary focus:border-primary focus:outline-none";

export default function OddsSelector({ onApply }: OddsSelectorProps) {
  const [sport, setSport] = useState(SPORT_OPTIONS[0].value);
  const [data, setData] = useState<GamesResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [side, setSide] = useState<"home" | "away">("home");

  const load = async (targetSport: string) => {
    setLoading(true);
    setError(null);
    try {
      setData(await listGames(targetSport));
    } catch {
      setError("Could not load games. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load(sport);
     
  }, [sport]);

  const applyGame = (gameId: string) => {
    if (!data) return;
    const game = data.games.find((g) => g.game_id === gameId);
    if (!game || !game.home_team || !game.away_team) return;
    const prices = bestPricesForSides(game);
    const chosen = side === "home" ? prices.home : prices.away;
    if (chosen !== null) onApply(chosen, game);
  };

  return (
    <div data-testid="odds-selector" className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-text-muted">
          Live odds
        </h2>
        <LiveOddsBadge stale={data ? data.stale : null} />
      </div>

      <div className="flex gap-2">
        <select
          aria-label="Sport"
          value={sport}
          onChange={(e) => setSport(e.target.value)}
          className={inputClass}
        >
          {SPORT_OPTIONS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
        <button
          type="button"
          onClick={() => void load(sport)}
          className="rounded-md border border-border px-3 py-2 text-sm text-text-secondary hover:text-text-primary"
        >
          Refresh
        </button>
      </div>

      {loading && (
        <p role="status" data-testid="odds-loading" className="text-xs text-text-muted">
          Loading games...
        </p>
      )}
      {error && (
        <p role="alert" data-testid="odds-error" className="text-xs text-danger">
          {error}
        </p>
      )}
      {data && !loading && data.games.length === 0 && !error && (
        <p data-testid="odds-empty" className="text-xs text-text-muted">
          No games stored for this sport. Refresh with an API key configured to fetch live odds.
        </p>
      )}

      {data && data.games.length > 0 && (
        <>
          <select
            aria-label="Game"
            defaultValue=""
            onChange={(e) => {
              if (e.target.value) applyGame(e.target.value);
              e.target.value = "";
            }}
            className={inputClass}
          >
            <option value="" disabled>
              Pick a game to use its odds...
            </option>
            {data.games.map((g) => {
              const p = bestPricesForSides(g);
              return (
                <option key={g.game_id} value={g.game_id}>
                  {g.away_team} ({p.away ?? "—"}) @ {g.home_team} ({p.home ?? "—"})
                </option>
              );
            })}
          </select>
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <span>Side:</span>
            {(["home", "away"] as const).map((s) => (
              <label key={s} className="flex items-center gap-1">
                <input
                  type="radio"
                  name="odds-side"
                  checked={side === s}
                  onChange={() => setSide(s)}
                />
                {s}
              </label>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
