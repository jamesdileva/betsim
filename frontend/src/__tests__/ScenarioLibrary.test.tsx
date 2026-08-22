import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ScenarioLibrary from "../components/ScenarioLibrary";
import { SCENARIOS } from "../data/scenarios";

describe("ScenarioLibrary", () => {
  it("lists all pre-built scenarios", () => {
    render(<ScenarioLibrary onApply={vi.fn()} />);
    const select = screen.getByLabelText(/Load a scenario/i) as HTMLSelectElement;
    const options = [...select.options].filter((o) => o.value !== "");
    expect(options).toHaveLength(SCENARIOS.length);
    expect(screen.getByText(/NFL Favorite -3 @ -110/)).toBeInTheDocument();
  });

  it("applies the chosen scenario params", async () => {
    const onApply = vi.fn();
    render(<ScenarioLibrary onApply={onApply} />);
    await userEvent.selectOptions(
      screen.getByLabelText(/Load a scenario/i),
      "mma-underdog",
    );
    expect(onApply).toHaveBeenCalledTimes(1);
    const applied = onApply.mock.calls[0][0];
    expect(applied.id).toBe("mma-underdog");
    expect(applied.params.odds_american).toBe(200);
  });

  it("resets the dropdown after applying so it can be reused", async () => {
    render(<ScenarioLibrary onApply={vi.fn()} />);
    const select = screen.getByLabelText(/Load a scenario/i) as HTMLSelectElement;
    await userEvent.selectOptions(select, "kelly-grinder");
    expect(select.value).toBe("");
  });
});
