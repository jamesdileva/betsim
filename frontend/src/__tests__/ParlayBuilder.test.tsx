import { useState } from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import ParlayBuilder from "../components/ParlayBuilder";
import { DEFAULT_LEG } from "../types/parlay";

describe("ParlayBuilder", () => {
  it("renders one section per leg with odds and probability inputs", () => {
    const legs = [{ ...DEFAULT_LEG }, { ...DEFAULT_LEG }, { ...DEFAULT_LEG }];
    render(<ParlayBuilder legs={legs} onChange={vi.fn()} />);
    expect(screen.getByTestId("parlay-leg-0")).toBeInTheDocument();
    expect(screen.getByTestId("parlay-leg-2")).toBeInTheDocument();
    expect(screen.getByLabelText("Odds for leg 3")).toHaveValue(-110);
  });

  it("adds a leg up to the max of 6", async () => {
    let legs = [{ ...DEFAULT_LEG }, { ...DEFAULT_LEG }];
    const onChange = (next: typeof legs) => {
      legs = next;
      rerender(<ParlayBuilder legs={legs} onChange={onChange} />);
    };
    const { rerender } = render(<ParlayBuilder legs={legs} onChange={onChange} />);

    for (let i = 0; i < 5; i++) {
      await userEvent.click(screen.getByTestId("add-leg"));
    }
    expect(screen.getAllByLabelText(/^Odds for leg/)).toHaveLength(6);
    expect(screen.getByTestId("add-leg")).toBeDisabled();
  });

  it("removes a leg but never below two", async () => {
    let legs = [{ ...DEFAULT_LEG }, { ...DEFAULT_LEG }, { ...DEFAULT_LEG }];
    const onChange = (next: typeof legs) => {
      legs = next;
      rerender(<ParlayBuilder legs={legs} onChange={onChange} />);
    };
    const { rerender } = render(<ParlayBuilder legs={legs} onChange={onChange} />);

    await userEvent.click(screen.getByTestId("remove-leg-0"));
    expect(screen.getAllByLabelText(/^Odds for leg/)).toHaveLength(2);
    expect(screen.queryByTestId(/remove-leg/)).not.toBeInTheDocument();
  });

  it("propagates edits to onChange", async () => {
    function Wrapper() {
      const [legs, setLegs] = useState([ { ...DEFAULT_LEG }, { ...DEFAULT_LEG } ]);
      return <ParlayBuilder legs={legs} onChange={setLegs} />;
    }
    render(<Wrapper />);
    const probInput = screen.getByLabelText("Win probability for leg 1");
    await userEvent.clear(probInput);
    await userEvent.type(probInput, "60");
    expect(probInput).toHaveValue(60);
  });
});

