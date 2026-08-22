import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Analytics from "../pages/Analytics";
import { getPerformance, runBacktests } from "../services/analyticsApi";
import type { PerformanceResponse } from "../types/analytics";

vi.mock("../services/analyticsApi");

const EMPTY: PerformanceResponse = { summary: [], evaluations: {} };

const WITH_DATA: PerformanceResponse = {
  summary: [
    { model_id: "m1", backtest_count: 12, accuracy: 0.5833, avg_roi: 0.021 },
  ],
  evaluations: {
    m1: [
      {
        id: 1,
        evaluated_at: "2026-08-22T10:00:00Z",
        accuracy: 0.5833,
        calibration_error: 0.031,
        brier_score: 0.2421,
        avg_roi: 0.021,
        notes: "Backtest over 12 games",
      },
    ],
  },
};

function renderPage() {
  return render(
    <MemoryRouter>
      <Analytics />
    </MemoryRouter>,
  );
}

describe("Analytics page", () => {
  beforeEach(() => {
    vi.mocked(getPerformance).mockResolvedValue(EMPTY);
    vi.mocked(runBacktests).mockResolvedValue({ backtests_created: 5 });
  });

  it("shows the empty state when nothing has been backtested", async () => {
    renderPage();
    expect(await screen.findByTestId("analytics-empty")).toBeInTheDocument();
  });

  it("renders summary and evaluation history after a run", async () => {
    vi.mocked(getPerformance)
      .mockResolvedValueOnce(EMPTY)
      .mockResolvedValueOnce(WITH_DATA);
    renderPage();
    await screen.findByTestId("analytics-empty");

    await userEvent.click(screen.getByTestId("run-backtests"));
    expect(await screen.findByTestId("summary-m1")).toBeInTheDocument();
    expect(screen.getAllByText("58.3%").length).toBe(2); // summary + history row
    expect(screen.getByTestId("evaluations-m1")).toBeInTheDocument();
    expect(screen.getByTestId("analytics-last-run")).toHaveTextContent(
      "5 backtests recorded",
    );
  });

  it("shows an error when loading fails", async () => {
    vi.mocked(getPerformance).mockRejectedValue(new Error("down"));
    renderPage();
    await waitFor(() =>
      expect(screen.getByTestId("analytics-error")).toBeInTheDocument(),
    );
  });
});
