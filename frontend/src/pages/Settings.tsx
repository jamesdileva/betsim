import { useEffect, useState } from "react";
import { loadSettings, saveSettings, type BetsimSettings } from "../services/settings";

export default function Settings() {
  const [settings, setSettings] = useState<BetsimSettings>(loadSettings);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!saved) return;
    const timer = setTimeout(() => setSaved(false), 2000);
    return () => clearTimeout(timer);
  }, [saved]);

  const update = (key: keyof BetsimSettings) => (value: number) =>
    setSettings((prev) => ({ ...prev, [key]: value }));

  const handleSave = (event: React.FormEvent) => {
    event.preventDefault();
    saveSettings(settings);
    setSaved(true);
  };

  const inputClass =
    "w-32 rounded-md border border-border bg-bg-tertiary px-3 py-2 text-text-primary focus:border-primary focus:outline-none";
  const labelClass = "text-sm text-text-secondary";

  return (
    <div className="mx-auto max-w-xl p-6">
      <h1 className="mb-6 text-lg font-bold">Settings</h1>
      <form
        onSubmit={handleSave}
        aria-label="Settings"
        className="space-y-4 rounded-lg border border-border bg-bg-secondary p-5"
      >
        <div className="flex items-center justify-between">
          <label htmlFor="default-simulations" className={labelClass}>
            Default simulations (100–100,000)
          </label>
          <input
            id="default-simulations"
            type="number"
            min={100}
            max={100000}
            value={settings.defaultSimulations}
            onChange={(e) => update("defaultSimulations")(Number(e.target.value))}
            className={inputClass}
          />
        </div>
        <div className="flex items-center justify-between">
          <label htmlFor="default-bankroll" className={labelClass}>
            Default bankroll ($)
          </label>
          <input
            id="default-bankroll"
            type="number"
            min={1}
            value={settings.defaultBankroll}
            onChange={(e) => update("defaultBankroll")(Number(e.target.value))}
            className={inputClass}
          />
        </div>
        <div className="flex items-center justify-between">
          <label htmlFor="default-bets" className={labelClass}>
            Default bets per run
          </label>
          <input
            id="default-bets"
            type="number"
            min={1}
            value={settings.defaultBets}
            onChange={(e) => update("defaultBets")(Number(e.target.value))}
            className={inputClass}
          />
        </div>
        <div className="flex items-center gap-3">
          <button
            type="submit"
            className="rounded-md bg-primary px-4 py-2 font-semibold text-bg-primary hover:bg-primary-hover"
          >
            Save Settings
          </button>
          {saved && (
            <span role="status" data-testid="settings-saved" className="text-sm text-success">
              Saved.
            </span>
          )}
        </div>
      </form>
      <p className="mt-4 text-xs text-text-muted">
        Preferences are stored locally on this machine. API keys and data-source settings arrive in a later sprint.
      </p>
    </div>
  );
}
