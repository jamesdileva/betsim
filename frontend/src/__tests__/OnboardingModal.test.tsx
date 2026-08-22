import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import OnboardingModal from "../components/OnboardingModal";

describe("OnboardingModal", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("walks through all steps then completes", async () => {
    const onComplete = vi.fn();
    render(<OnboardingModal onComplete={onComplete} />);

    expect(screen.getByRole("dialog", { name: "Onboarding" })).toBeInTheDocument();

    // steps 1-3: click Next
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    await userEvent.click(screen.getByRole("button", { name: "Next" }));

    const finish = screen.getByRole("button", { name: "Try it yourself" });
    await userEvent.click(finish);
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it("shows progress dots advancing", async () => {
    render(<OnboardingModal onComplete={vi.fn()} />);
    expect(screen.getByTestId("onboarding-dot-0")).toHaveClass("bg-primary");
    expect(screen.getByTestId("onboarding-dot-3")).not.toHaveClass("bg-primary");
    await userEvent.click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByTestId("onboarding-dot-1")).toHaveClass("bg-primary");
  });
});
