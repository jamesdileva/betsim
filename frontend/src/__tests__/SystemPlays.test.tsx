import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import SystemPlays from "../pages/SystemPlays";
import { calibrate } from "../services/systemPlaysApi";
import type { CalibrationReport } from "../types/systemPlays";

vi.mock("../services/systemPlaysApi");

const REPORT: CalibrationReport = {
  stated_probability: 0.6,
  actual_win_rate: 0.5987,
  calibration_error: 0.0013,
  calibration_status: "well_calibrated",
  confidence_interval_low: 0.58,
  confidence_interval_high: 0.62,
  recommendation: "Well calibrated.",
};

function renderPage() {
  return render(
    <MemoryRouter>
      <SystemPlays />
    </MemoryRouter>,
  );
}

describe("SystemPlays page", () => {
  beforeEach(() => {
    vi.mocked(calibrate).mockResolvedValue(REPORT);
  });

  it("shows placeholder before running", () => {
    renderPage();
    expect(screen.getByTestId("calibration-placeholder")).toBeInTheDocument();
  });

  it("submits the form values to the calibration API", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "Calibrate Model" }));
    await waitFor(() => expect(screen.getByTestId("report-status")).toBeInTheDocument());
    expect(vi.mocked(calibrate)).toHaveBeenCalledWith(
      expect.objectContaining({
        odds_american: -110,
        win_probability: 0.6,
        bankroll: 1000,
        bet_size: 100,
        bet_size_type: "flat",
        num_bets: 100,
        num_simulations: 5000,
      }),
    );
  });

  it("renders the report after success", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "Calibrate Model" }));
    await waitFor(() =>
      expect(screen.getByTestId("report-stated")).toHaveTextContent("60.00%"),
    );
  });

  it("shows an error message when the API fails", async () => {
    vi.mocked(calibrate).mockRejectedValue(new Error("backend down"));
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: "Calibrate Model" }));
    await waitFor(() => expect(screen.getByTestId("calibration-error")).toBeInTheDocument());
  });
});
