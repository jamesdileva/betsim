import { useState } from "react";
import { Route, Routes, useLocation } from "react-router-dom";
import Navigation from "./components/Navigation";
import OnboardingModal from "./components/OnboardingModal";
import ParlaySimulator from "./pages/ParlaySimulator";
import ResultsHistory from "./pages/ResultsHistory";
import Settings from "./pages/Settings";
import Strategies from "./pages/Strategies";
import SimulationWorkspace from "./pages/SimulationWorkspace";
import SystemPlays from "./pages/SystemPlays";
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
          <Route path="/strategies" element={<Strategies />} />
          <Route path="/history" element={<ResultsHistory />} />
          <Route path="/system-plays" element={<SystemPlays />} />
          <Route path="/parlay" element={<ParlaySimulator />} />
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
