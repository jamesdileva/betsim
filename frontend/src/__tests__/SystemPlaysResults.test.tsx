import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SystemPlaysResults from "../components/SystemPlaysResults";
import type { CalibrationReport } from "../types/systemPlays";

function reportWith(overrides: Partial<CalibrationReport>): CalibrationReport {
  return {
    stated_probability: 0.7,
    actual_win_rate: 0.6,
    calibration_error: 0.1,
    calibration_status: "overconfident",
    confidence_interval_low: 0.57,
    confidence_interval_high: 0.63,
    recommendation: "Your model overestimates probability by ~10%. Consider adjusting.",
    ...overrides,
  };
}

describe("SystemPlaysResults", () => {
  it("shows stated vs actual vs error with two decimals", () => {
    render(<SystemPlaysResults report={reportWith({})} />);
    expect(screen.getByTestId("report-stated")).toHaveTextContent("70.00%");
    expect(screen.getByTestId("report-actual")).toHaveTextContent("60.00%");
    expect(screen.getByTestId("report-error")).toHaveTextContent("10.00%");
  });

  it("colors status by calibration outcome", () => {
    const { rerender } = render(
      <SystemPlaysResults report={reportWith({ calibration_status: "well_calibrated" })} />,
    );
    expect(screen.getByTestId("report-status")).toHaveClass("text-success");

    rerender(<SystemPlaysResults report={reportWith({ calibration_status: "underconfident" })} />);
    expect(screen.getByTestId("report-status")).toHaveClass("text-warning");

    rerender(<SystemPlaysResults report={reportWith({ calibration_status: "overconfident" })} />);
    expect(screen.getByTestId("report-status")).toHaveClass("text-danger");
  });

  it("displays the confidence interval and recommendation", () => {
    render(
      <SystemPlaysResults
        report={reportWith({
          confidence_interval_low: 0.57,
          confidence_interval_high: 0.63,
        })}
      />,
    );
    expect(screen.getByTestId("report-ci")).toHaveTextContent("[57.00% — 63.00%]");
    expect(screen.getByTestId("report-recommendation")).toHaveTextContent(/overestimates/);
    expect(screen.getByTestId("calibration-chart")).toBeInTheDocument();
  });
});
