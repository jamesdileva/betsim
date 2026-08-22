import { describe, expect, it } from "vitest";
import { kellyFraction } from "./kelly";

describe("kellyFraction", () => {
  it("matches the backend formula for -110 at 55%", () => {
    // b = 1.9091 - 1; (b*0.55 - 0.45)/b ~= 0.055
    expect(kellyFraction(-110, 0.55)).toBeCloseTo(0.055, 4);
  });

  it("returns 0.2 for even money at 60%", () => {
    expect(kellyFraction(100, 0.6)).toBeCloseTo(0.2, 6);
  });

  it("returns zero when there is no edge", () => {
    expect(kellyFraction(-110, 0.5)).toBe(0);
    expect(kellyFraction(-200, 0.3)).toBe(0);
  });

  it("returns zero on degenerate inputs", () => {
    expect(kellyFraction(-110, 0)).toBe(0);
    expect(kellyFraction(-110, 1)).toBe(0);
  });

  it("handles plus money", () => {
    // decimal 2.5 (b=1.5), p=0.45 -> (1.5*0.45 - 0.55)/1.5 = 0.08333
    expect(kellyFraction(150, 0.45)).toBeCloseTo(0.08333, 4);
  });
});
