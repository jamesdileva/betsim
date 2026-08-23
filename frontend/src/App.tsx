import { Route, Routes } from "react-router-dom";
import Analytics from "./pages/Analytics";
import Navigation from "./components/Navigation";
import ParlaySimulator from "./pages/ParlaySimulator";
import PortfolioPage from "./pages/Portfolio";
import ResultsHistory from "./pages/ResultsHistory";
import Settings from "./pages/Settings";
import Strategies from "./pages/Strategies";
import SimulationWorkspace from "./pages/SimulationWorkspace";
import SystemPlays from "./pages/SystemPlays";

// Onboarding lives in SimulationWorkspace (it pre-fills the form on
// "Try it yourself"), which is the "/" route.
export default function App() {
  return (
    <div className="flex h-full flex-col">
      <Navigation />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<SimulationWorkspace />} />
          <Route path="/strategies" element={<Strategies />} />
          <Route path="/history" element={<ResultsHistory />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/system-plays" element={<SystemPlays />} />
          <Route path="/parlay" element={<ParlaySimulator />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<p className="p-6 text-text-muted">Page not found.</p>} />
        </Routes>
      </main>
    </div>
  );
}
