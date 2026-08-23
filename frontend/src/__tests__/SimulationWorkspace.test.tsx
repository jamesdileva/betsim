import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import SimulationWorkspace from "../pages/SimulationWorkspace";

vi.mock("../services/api", () => ({
  default: { post: vi.fn().mockResolvedValue({ data: {} }), get: vi.fn() },
}));

function renderWorkspace() {
  return render(
    <MemoryRouter>
      <SimulationWorkspace />
    </MemoryRouter>,
  );
}

async function completeOnboardingViaTryIt() {
  for (let i = 0; i < 3; i++) {
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
  }
  await userEvent.click(screen.getByRole("button", { name: "Try it yourself" }));
}

describe("SimulationWorkspace onboarding pre-fill", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("pre-fills the form with the NFL Favorite example via Try it yourself", async () => {
    renderWorkspace();
    await screen.findByRole("dialog", { name: "Onboarding" });

    await completeOnboardingViaTryIt();

    await waitFor(() =>
      expect(screen.queryByRole("dialog", { name: "Onboarding" })).not.toBeInTheDocument(),
    );
    // NFL Favorite scenario: -110 @ 65% (form default is 55%)
    expect(screen.getByLabelText("Win probability (%)")).toHaveValue(65);
    // completion flag persists
    expect(localStorage.getItem("betsim.onboardingCompleted")).toBe("true");
  });

  it("does not show the walkthrough when previously completed", async () => {
    localStorage.setItem("betsim.onboardingCompleted", "true");
    renderWorkspace();
    await waitFor(() =>
      expect(screen.getByTestId("results-placeholder")).toBeInTheDocument(),
    );
    expect(screen.queryByRole("dialog", { name: "Onboarding" })).not.toBeInTheDocument();
  });
});
