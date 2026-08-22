import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LiveOddsBadge from "../components/LiveOddsBadge";

describe("LiveOddsBadge", () => {
  it("shows Live when data is fresh", () => {
    render(<LiveOddsBadge stale={false} />);
    expect(screen.getByTestId("odds-badge")).toHaveTextContent("Live");
  });

  it("shows Stale after the 2h threshold", () => {
    render(<LiveOddsBadge stale />);
    expect(screen.getByTestId("odds-badge")).toHaveTextContent("Stale");
  });

  it("explains when odds were never fetched", () => {
    render(<LiveOddsBadge stale={null} />);
    expect(screen.getByTestId("odds-badge")).toHaveTextContent("No odds fetched");
  });
});
