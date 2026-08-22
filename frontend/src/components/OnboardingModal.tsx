import { useState } from "react";

interface OnboardingModalProps {
  onComplete: () => void;
}

const STEPS = [
  {
    title: "Welcome to Betsim",
    body: "Betsim is a Monte Carlo betting simulator. It doesn't predict winners — it shows you what happens to your bankroll when you place bets with a given edge.",
  },
  {
    title: "Step 1: Set your bet",
    body: "Enter the odds (e.g. -110), your estimated win probability, and how much of your bankroll you bet each time. Your edge is the difference between your probability and what the odds imply.",
  },
  {
    title: "Step 2: Run the simulation",
    body: "Click Run Simulation and Betsim plays out your strategy thousands of times, so you can see win rates, expected value, and — most importantly — how often you'd go broke.",
  },
  {
    title: "Variance is real",
    body: "Even a winning bettor can go broke with poor bankroll management. Watch the risk of ruin number — that's the lesson.",
  },
];

export default function OnboardingModal({ onComplete }: OnboardingModalProps) {
  const [step, setStep] = useState(0);
  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Onboarding"
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
    >
      <div className="w-full max-w-md rounded-lg border border-border bg-bg-secondary p-6">
        <h2 className="mb-3 text-xl font-bold text-primary">{current.title}</h2>
        <p className="mb-6 text-text-secondary">{current.body}</p>
        <div className="flex items-center justify-between">
          <div className="flex gap-1" aria-hidden="true">
            {STEPS.map((_, i) => (
              <span
                key={i}
                data-testid={`onboarding-dot-${i}`}
                className={`h-2 w-2 rounded-full ${i <= step ? "bg-primary" : "bg-bg-tertiary"}`}
              />
            ))}
          </div>
          {isLast ? (
            <button
              type="button"
              onClick={onComplete}
              className="rounded-md bg-primary px-4 py-2 font-semibold text-bg-primary hover:bg-primary-hover"
            >
              Try it yourself
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setStep(step + 1)}
              className="rounded-md bg-primary px-4 py-2 font-semibold text-bg-primary hover:bg-primary-hover"
            >
              Next
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
