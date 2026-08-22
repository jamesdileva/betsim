import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "../App";

describe("App", () => {
  it("renders navigation and workspace by default", () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByRole("navigation", { name: "Main navigation" })).toBeInTheDocument();
    expect(screen.getByText("Bet parameters")).toBeInTheDocument();
  });

  it("routes to the settings page", () => {
    render(
      <MemoryRouter initialEntries={["/settings"]}>
        <App />
      </MemoryRouter>,
    );
    expect(screen.getByRole("form", { name: "Settings" })).toBeInTheDocument();
  });
});
