import { renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as apiModule from "../services/strategiesApi";
import { useStrategies } from "../hooks/useStrategies";

vi.mock("../services/strategiesApi");

const mocked = vi.mocked(apiModule);

describe("useStrategies", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("loads strategies on mount", async () => {
    const strategy = { id: 1, name: "A" } as never;
    mocked.listStrategies.mockResolvedValue([strategy]);
    const { result } = renderHook(() => useStrategies());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.strategies).toHaveLength(1);
    expect(result.current.error).toBeNull();
  });

  it("sets an error message when loading fails", async () => {
    mocked.listStrategies.mockRejectedValue(new Error("network down"));
    const { result } = renderHook(() => useStrategies());
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toMatch(/Could not load strategies/);
  });

  it("save prepends the created strategy", async () => {
    const created = { id: 9, name: "New" } as never;
    mocked.listStrategies.mockResolvedValue([]);
    mocked.createStrategy.mockResolvedValue(created);
    const { result } = renderHook(() => useStrategies());
    await waitFor(() => expect(result.current.loading).toBe(false));

    await result.current.save({
      name: "New",
      odds_american: -110,
      win_probability: 0.55,
      bankroll: 1000,
      bet_size: 50,
      bet_size_type: "flat",
      num_bets: 100,
      num_simulations: 5000,
    });
    expect(mocked.createStrategy).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(result.current.strategies.map((s) => s.id)).toEqual([9]));
  });

  it("remove filters out the deleted strategy", async () => {
    const a = { id: 1, name: "A" } as never;
    const b = { id: 2, name: "B" } as never;
    mocked.listStrategies.mockResolvedValue([a, b]);
    mocked.deleteStrategy.mockResolvedValue(undefined);
    const { result } = renderHook(() => useStrategies());
    await waitFor(() => expect(result.current.strategies).toHaveLength(2));

    await result.current.remove(1);
    await waitFor(() => expect(result.current.strategies.map((s) => s.id)).toEqual([2]));
  });
});
