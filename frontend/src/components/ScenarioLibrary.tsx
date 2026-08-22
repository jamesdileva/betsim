import { SCENARIOS, type Scenario } from "../data/scenarios";

interface ScenarioLibraryProps {
  onApply: (scenario: Scenario) => void;
}

export default function ScenarioLibrary({ onApply }: ScenarioLibraryProps) {
  return (
    <div data-testid="scenario-library">
      <label htmlFor="scenario-select" className="mb-1 block text-sm text-text-secondary">
        Load a scenario
      </label>
      <select
        id="scenario-select"
        defaultValue=""
        onChange={(event) => {
          const scenario = SCENARIOS.find((s) => s.id === event.target.value);
          if (scenario) {
            onApply(scenario);
            event.target.value = "";
          }
        }}
        className="w-full rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary focus:border-primary focus:outline-none"
      >
        <option value="" disabled>
          Choose a pre-built scenario...
        </option>
        {SCENARIOS.map((scenario) => (
          <option key={scenario.id} value={scenario.id}>
            {scenario.name} — {scenario.description}
          </option>
        ))}
      </select>
    </div>
  );
}
