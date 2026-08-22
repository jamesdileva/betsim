import { describe, expect, it, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import App from "../App";
import api from "../services/api";

vi.mock("../services/api");

describe("App", () => {
  it("shows connected status when backend is healthy", async () => {
    vi.mocked(api.get).mockResolvedValue({ data: { status: "ok" } });
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId("connection-status")).toHaveTextContent("Connected");
    });
    expect(api.get).toHaveBeenCalledWith("/health");
  });

  it("shows error status when backend is unreachable", async () => {
    vi.mocked(api.get).mockRejectedValue(new Error("connection refused"));
    render(<App />);
    await waitFor(() => {
      expect(screen.getByTestId("connection-status")).toHaveTextContent("Backend unreachable");
    });
  });
});
