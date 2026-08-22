import { BET_SIZE_TYPES } from "./SimulationForm";
import type { BetSizeType } from "../types/simulation";

interface BankrollStrategySelectorProps {
  value: BetSizeType;
  onChange: (value: BetSizeType) => void;
}

export default function BankrollStrategySelector({
  value,
  onChange,
}: BankrollStrategySelectorProps) {
  return (
    <fieldset data-testid="bankroll-strategy-selector">
      <legend className="mb-1 text-sm text-text-secondary">Bet strategy</legend>
      <div className="flex flex-wrap gap-3">
        {BET_SIZE_TYPES.map((type) => (
          <label key={type.value} className="flex items-center gap-1.5 text-sm text-text-secondary">
            <input
              type="radio"
              name="bankroll-strategy"
              value={type.value}
              checked={value === type.value}
              onChange={() => onChange(type.value as BetSizeType)}
            />
            {type.label}
          </label>
        ))}
      </div>
    </fieldset>
  );
}
