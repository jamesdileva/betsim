import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import OddsSelector from "../components/OddsSelector";
import { listGames } from "../services/oddsApi";
import type { GamesResponse } from "../types/odds";

vi.mock("../services/oddsApi");

const RESPONSE: GamesResponse = {
  sport: "americanfootball_nfl",
  stale: false,
  games: [
    {
      game_id: "g1",
      sport: "americanfootball_nfl",
      home_team: "Chiefs",
      away_team: "Bills",
      game_time: null,
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
          sportsbook: "draftkings",
          outcome_name: "Bills",
          market_type: "moneyline",
          odds_american: 130,
          odds_decimal: 2.3,
          implied_probability: 0.435,
          timestamp: "2026-08-22T12:00:00",
        },
      ],
    },
  ],
};

describe("OddsSelector", () => {
  beforeEach(() => {
    vi.mocked(listGames).mockResolvedValue(RESPONSE);
  });

  it("loads games and shows the live badge", async () => {
    render(<OddsSelector onApply={vi.fn()} />);
    await waitFor(() =>
      expect(screen.getByText(/Bills \(130\) @ Chiefs \(-150\)/)).toBeInTheDocument(),
    );
    expect(screen.getByTestId("odds-badge")).toHaveTextContent("Live");
  });

  it("applies home-side odds for the chosen game", async () => {
    const onApply = vi.fn();
    render(<OddsSelector onApply={onApply} />);
    await screen.findByLabelText("Game");
    // default side is home
    await userEvent.selectOptions(screen.getByLabelText("Game"), "g1");
    expect(onApply).toHaveBeenCalledTimes(1);
    const [odds] = onApply.mock.calls[0];
    expect(odds).toBe(-150);
  });

  it("applies away-side odds after switching side", async () => {
    const onApply = vi.fn();
    render(<OddsSelector onApply={onApply} />);
    await screen.findByLabelText("Game");
    await userEvent.click(screen.getByLabelText("away"));
    await userEvent.selectOptions(screen.getByLabelText("Game"), "g1");
    expect(onApply).toHaveBeenCalledWith(130, expect.objectContaining({ game_id: "g1" }));
  });

  it("shows an empty state when no games exist", async () => {
    vi.mocked(listGames).mockResolvedValue({ ...RESPONSE, games: [], stale: true });
    render(<OddsSelector onApply={vi.fn()} />);
    expect(await screen.findByTestId("odds-empty")).toBeInTheDocument();
    expect(screen.getByTestId("odds-badge")).toHaveTextContent("Stale");
  });
});
