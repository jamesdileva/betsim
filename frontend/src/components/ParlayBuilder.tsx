import { DEFAULT_LEG, type ParlayLegInput } from "../types/parlay";

interface ParlayBuilderProps {
  legs: ParlayLegInput[];
  onChange: (legs: ParlayLegInput[]) => void;
  maxLegs?: number;
}

const inputClass =
  "w-full rounded-md border border-border bg-bg-tertiary px-2.5 py-1.5 text-sm text-text-primary focus:border-primary focus:outline-none";

function legValid(leg: ParlayLegInput): boolean {
  const odds = Number(leg.oddsAmerican);
  const prob = Number(leg.winProbabilityPct);
  return (
    odds !== 0 && Math.abs(odds) >= 100 && prob > 0 && prob < 100 && !Number.isNaN(prob)
  );
}

export default function ParlayBuilder({ legs, onChange, maxLegs = 6 }: ParlayBuilderProps) {
  const update = (index: number, key: keyof ParlayLegInput) => (value: string) =>
    onChange(legs.map((leg, i) => (i === index ? { ...leg, [key]: value } : leg)));

  return (
    <div data-testid="parlay-builder" className="space-y-3">
      {legs.map((leg, i) => (
        <div
          key={i}
          data-testid={`parlay-leg-${i}`}
          className="rounded-md border border-border bg-bg-tertiary/40 p-3"
        >
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wide text-text-muted">
              Leg {i + 1}
            </span>
            {legs.length > 2 && (
              <button
                type="button"
                aria-label={`Remove leg ${i + 1}`}
                data-testid={`remove-leg-${i}`}
                onClick={() => onChange(legs.filter((_, j) => j !== i))}
                className="text-xs text-danger hover:opacity-80"
              >
                Remove
              </button>
            )}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="mb-1 block text-xs text-text-secondary">Odds</span>
              <input
                type="number"
                value={leg.oddsAmerican}
                aria-label={`Odds for leg ${i + 1}`}
                onChange={(e) => update(i, "oddsAmerican")(e.target.value)}
                className={`${inputClass} ${!legValid(leg) ? "border-danger" : ""}`}
              />
            </label>
            <label className="block">
              <span className="mb-1 block text-xs text-text-secondary">Win prob (%)</span>
              <input
                type="number"
                value={leg.winProbabilityPct}
                aria-label={`Win probability for leg ${i + 1}`}
                onChange={(e) => update(i, "winProbabilityPct")(e.target.value)}
                className={`${inputClass} ${!legValid(leg) ? "border-danger" : ""}`}
              />
            </label>
          </div>
        </div>
      ))}

      <button
        type="button"
        disabled={legs.length >= maxLegs}
        data-testid="add-leg"
        onClick={() => onChange([...legs, { ...DEFAULT_LEG }])}
        className={`w-full rounded-md border border-dashed border-border px-4 py-2 text-sm ${
          legs.length >= maxLegs
            ? "cursor-not-allowed text-text-muted"
            : "text-text-secondary hover:border-primary hover:text-primary"
        }`}
      >
        + Add Selection ({legs.length}/{maxLegs})
      </button>
    </div>
  );
}
