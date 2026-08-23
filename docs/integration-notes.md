# Betsim × Sentinel Integration Notes

Verified ground truth for wiring betsim into Sentinel (see Sentinel's
`docs/integration.md`). Facts below were verified live on 2026-08-22 against
the packaged build at `release/win-unpacked/Betsim.exe`.

## Verified ground truth

```
Verified ground truth (2026-08-22):
- launch: FeatureRunner-owned (electron engine). The packaged exe is
  release/win-unpacked/Betsim.exe; it spawns its OWN backend
  (.venv uvicorn, port 8000) when a sibling .venv exists, waits for
  /api/health, then loads the renderer. No separate startup command needed.
- port 8000, no auth (GET /api/health -> {"status": "ok"})
- fallback: without a sibling .venv the UI renders fully but shows
  "Backend unreachable" - features fail honestly rather than vacuously
- sandbox: --user-data-dir passed by the CDP runner doubles as the database
  sandbox (BETSIM_DB_PATH=<user-data-dir>/betsim.db), so every run starts
  on a fresh DB; cleanup = taskkill /IM Betsim.exe /T (tree kill takes
  the spawned uvicorn down)
- window title "Betsim" (renderer <title>); informational only - electron
  features attach over CDP and do not use it
```

## Registry facts

| Key | Value |
|-----|-------|
| Project slug | `Betsim` (DB row `name='Betsim'`, path `C:\Users\j\Projects\betsim` — casing verified live; see ResMaker lesson in `features/__init__.py`) |
| Engine | Tier 2, `electron=True`, feature-only (no smoke tester; assertions are UI-side) |
| Features | ① workspace simulation end-to-end (dismiss onboarding → Run Simulation → assert metric cards + charts); ② screen tour across all tabs |
| Test command (Tier 0 gate) | root `npm test` → pytest (backend, ~7s) + vitest (frontend, ~10s) |

## Gotchas encoded in the packaging

These were all real bugs hit while making the exe Sentinel-ready:

1. **`type: module` vs main process**: `frontend/package.json` declares
   `"type": "module"`, so the Electron main script must be `.cjs` or it
   crashes with "require is not defined in ES module scope" when packaged.
2. **Vite `base: "./"`**: default absolute asset URLs break under `file://`
   (blank white page).
3. **HashRouter**: `BrowserRouter` can never match under `file://`
   ("Page not found" on every tab).
4. **Repo-root detection**: derive from `app.getPath("exe")` (two levels up
   from `release/win-unpacked/`), never from `__dirname` (inside `app.asar`).
5. **CORS `Origin: null`**: a `file://` renderer sends Origin null;
   FastAPI CORS must allow it explicitly.
6. **Onboarding modal**: fresh sandbox localStorage ⇒ the walkthrough shows
   on `/` every run; features dismiss it deterministically first.
