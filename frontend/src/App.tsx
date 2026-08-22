import { useState } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import Navigation from "./components/Navigation";
import OnboardingModal from "./components/OnboardingModal";
import PlaceholderPage from "./pages/PlaceholderPage";
import Settings from "./pages/Settings";
import SimulationWorkspace from "./pages/SimulationWorkspace";
import { completeOnboarding, hasCompletedOnboarding } from "./services/settings";

export default function App() {
  const [onboardingDone, setOnboardingDone] = useState(hasCompletedOnboarding);
  const location = useLocation();

  return (
    <div className="flex h-full flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<SimulationWorkspace />} />
          <Route
            path="/strategies"
            element={<PlaceholderPage title="Strategies" sprint="8" />}
          />
          <Route
            path="/system-plays"
            element={<PlaceholderPage title="System Plays" sprint="10" />}
          />
          <Route path="/parlay" element={<PlaceholderPage title="Parlay Simulator" sprint="11" />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<p className="p-6 text-text-muted">Page not found.</p>} />
        </Routes>
      </main>
      {!onboardingDone && location.pathname === "/" && (
        <OnboardingModal
          onComplete={() => {
            completeOnboarding();
            setOnboardingDone(true);
          }}
        />
      )}
    </div>
  );
}
