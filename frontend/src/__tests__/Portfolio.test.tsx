import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import PortfolioPage from "../pages/Portfolio";
import { buildPortfolio, getLatestPortfolio } from "../services/portfolioApi";
import type { Portfolio } from "../types/portfolio";

vi.mock("../services/portfolioApi");

function makePortfolio(overrides: Partial<Portfolio> = {}): Portfolio {
  return {
    id: 1,
    date: null,
    total_risk: 6,
    expected_roi: 8,
    kelly_exposure: 12,
    model_id: "m1",
    items: [
      {
        id: 10,
        portfolio_id: 1,
        game_id: "g-1",
        model_id: "m1",
        confidence_level: "high",
        bet_type: "moneyline",
        stake: 200,
        predicted_probability: 0.74,
        ev: 0.083,
        recommendation_stars: 4,
      },
      {
        id: 11,
        portfolio_id: 1,
        game_id: "g-2",
        model_id: "m1",
        confidence_level: "long_shot",
        bet_type: "moneyline",
        stake: 50,
        predicted_probability: 0.35,
        ev: -0.05,
        recommendation_stars: 2,
      },
    ],
    ...overrides,
  };
}

function renderPage() {
  return render(
    <MemoryRouter>
      <PortfolioPage />
    </MemoryRouter>,
  );
}

describe("Portfolio page", () => {
  beforeEach(() => {
    vi.mocked(getLatestPortfolio).mockResolvedValue(null);
    vi.mocked(buildPortfolio).mockResolvedValue(makePortfolio());
  });

  it("shows the empty state before any portfolio exists", async () => {
    renderPage();
    expect(await screen.findByTestId("portfolio-empty")).toBeInTheDocument();
  });

  it("builds a portfolio with the entered bankroll", async () => {
    renderPage();
    await screen.findByTestId("portfolio-empty");
    const bankroll = screen.getByLabelText("Bankroll ($)");
    await userEvent.clear(bankroll);
    await userEvent.type(bankroll, "2500");
    await userEvent.click(screen.getByTestId("build-portfolio"));

    await waitFor(() =>
      expect(screen.getByTestId("portfolio-view")).toBeInTheDocument(),
    );
    expect(vi.mocked(buildPortfolio)).toHaveBeenCalledWith(2500);
  });

  it("renders band sections and key metrics", async () => {
    vi.mocked(getLatestPortfolio).mockResolvedValue(makePortfolio());
    renderPage();
    await waitFor(() => expect(screen.getByTestId("portfolio-view")).toBeInTheDocument());

    expect(screen.getByTestId("band-high")).toBeInTheDocument();
    expect(screen.getByTestId("band-long_shot")).toBeInTheDocument();
    expect(screen.getByTestId("pf-total-risk")).toHaveTextContent("6%");
    expect(screen.getByTestId("pf-item-count")).toHaveTextContent("2");
    expect(screen.getByTestId("portfolio-item-10")).toHaveTextContent("$200");
  });

  it("surfaces API errors", async () => {
    vi.mocked(getLatestPortfolio).mockRejectedValue(new Error("down"));
    renderPage();
    await waitFor(() => expect(screen.getByTestId("portfolio-error")).toBeInTheDocument());
  });
});
