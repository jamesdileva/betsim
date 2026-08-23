import { NavLink } from "react-router-dom";

const LINKS = [
  { to: "/", label: "Simulation" },
  { to: "/strategies", label: "Strategies" },
  { to: "/history", label: "History" },
  { to: "/analytics", label: "Analytics" },
  { to: "/portfolio", label: "Portfolio" },
  { to: "/system-plays", label: "System Plays" },
  { to: "/parlay", label: "Parlay" },
  { to: "/settings", label: "Settings" },
];

export default function Navigation() {
  return (
    <nav
      aria-label="Main navigation"
      className="flex items-center gap-1 border-b border-border bg-bg-secondary px-4 py-2"
    >
      <span className="mr-4 text-lg font-bold text-primary">Betsim</span>
      {LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) =>
            `rounded-md px-3 py-1.5 text-sm ${
              isActive
                ? "bg-bg-tertiary font-semibold text-primary"
                : "text-text-secondary hover:text-text-primary"
            }`
          }
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
