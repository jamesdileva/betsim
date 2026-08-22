export interface BetsimSettings {
  defaultSimulations: number;
  defaultBankroll: number;
  defaultBets: number;
}

const SETTINGS_KEY = "betsim.settings.v1";
const ONBOARDING_KEY = "betsim.onboardingCompleted";

export const DEFAULT_SETTINGS: BetsimSettings = {
  defaultSimulations: 5000,
  defaultBankroll: 1000,
  defaultBets: 100,
};

export function loadSettings(): BetsimSettings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
  } catch {
    // fall through to defaults on parse failure
  }
  return DEFAULT_SETTINGS;
}

export function saveSettings(settings: BetsimSettings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

export function hasCompletedOnboarding(): boolean {
  return localStorage.getItem(ONBOARDING_KEY) === "true";
}

export function completeOnboarding(): void {
  localStorage.setItem(ONBOARDING_KEY, "true");
}
