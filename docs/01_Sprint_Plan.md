# Betsim Sprint Plan

**Project:** Betsim - Monte Carlo Betting Simulator  
**Approach:** Electron + FastAPI + SQLite (local-first desktop app)  
**Workflow:** 2-week sprints, MVP-focused, expand iteratively  
**Total Sprints:** 15 (Sprint 0–14)

---

## Sprint Overview

| Sprint | Name | Focus | Key Deliverable |
|--------|------|-------|-----------------|
| 0 | Foundation & Tooling | Project scaffold | Electron+FastAPI+SQLite running with CI |
| 1 | Database Schema | All tables + migrations | Full DB schema in SQLite, ORM ready |
| 2 | Monte Carlo Core | Simulation engine | Can run single + batch simulations |
| 3 | EV & Bankroll | Metrics + strategies | Risk of ruin, EV, Kelly, max drawdown |
| 4 | Repository Layer | CRUD operations | SQLAlchemy CRUD for all tables |
| 5 | Backend API | REST endpoints | All API endpoints documented + tested |
| 6 | Dashboard Framework | Sim workspace + UI basics | Dark mode, onboarding, settings, navigation |
| 7 | Visualization & Charting | Charts + scenarios | Bankroll trajectory, histogram, scenario library |
| 8 | Strategy Management & History | Save/load + history | Persist strategies, history browser, CSV export |
| 9 | Data Collection & Features | Odds API + features | Collect + normalize odds, feature schema |
| 10 | System Plays Engine | Model validation | Calibration engine, recommendation lifecycle |
| 11 | Parlay + Strategy Comparison | Bet types + comparison | Parlay builder, side-by-side strategy comparison |
| 12 | Backtesting Engine | Historical replay | Model evaluation, analytics dashboard |
| 13 | ML Pipeline & Explainability | Model infrastructure | Model interface, training pipeline, top factors |
| 14 | Intelligence Score, Portfolio & Testing | Scoring + QA | Intelligence score, portfolio, test suite, packaging |

---

## Sprint Format

Each sprint follows this structure:

| Section | Description |
|---------|-------------|
| **Purpose** | What problem this sprint solves |
| **Goal** | One sentence: what "done" looks like |
| **Why Now** | Why this sprint matters at this point in the sequence |
| **Background** | Context and technical details |
| **Deliverables** | Bullet list of what gets built |
| **Acceptance Criteria** | Standard checklist: lint, tests, e2e, docs |
| **Files / Folders** | Exact files to create/modify |
| **Database Changes** | Schema modifications for this sprint |
| **Backend Tasks** | Backend work items |
| **Frontend Tasks** | Frontend work items |
| **Tests** | What to test |
| **Verification Checklist** | Manual QA steps |
| **Definition of Done** | What "shippable" means for this sprint |
| **Out of Scope** | What we are NOT doing |
| **Next Sprint Dependencies** | What the next sprint needs from this one |

---

## Sprint 0 — Foundation & Tooling

### Purpose
Bootstrap the Electron + FastAPI + SQLite development environment with a clean, working scaffold. Establish conventions, CI, and IPC communication so both frontend and backend are independently runnable and connected.

### Goal
A repository where `npm run dev` launches an Electron window, and the Electron renderer can make a successful HTTP request to a locally running FastAPI server. SQLite database initializes automatically.

### Why Now
All subsequent sprints depend on a working scaffold. Without a runnable Electron window and responding FastAPI server, no feature can be built or tested. This sprint establishes the foundation, conventions, and CI that everything else builds on.

### Background
The app is a desktop application built with Electron (React frontend) and FastAPI (Python backend). SQLite stores strategies and simulation results. Communication happens via HTTP from Electron renderer to localhost:8000.

### Deliverables
- Electron app launches and displays a window
- FastAPI server starts and responds to `/health` with `{"status": "ok"}`
- SQLite database file created automatically on first run
- Root `package.json` with workspace scripts
- ESLint + Prettier configured on frontend
- `ruff` configured on backend
- GitHub Actions CI: runs lint + tests on push
- `.env.example` for API keys

### Acceptance Criteria
- [ ] Code committed and lint passes (`ruff check backend/`, `eslint frontend/src/`)
- [ ] Unit tests pass (`pytest`, `vitest`)
- [ ] Integration tests pass
- [ ] Feature works end-to-end in running Electron app
- [ ] Documentation updated (if schema/API changes)
- [ ] No critical bugs in QA

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `package.json` | CREATE | Root workspace, `dev` script runs both backend & electron |
| `electron-builder.json` | CREATE | Electron packaging config |
| `.gitignore` | CREATE | Ignores `node_modules/`, `__pycache__/`, `*.db`, dist folders |
| `.env.example` | CREATE | Template for API keys |
| `backend/main.py` | CREATE | FastAPI app with `/health` endpoint |
| `backend/config.py` | CREATE | Pydantic settings (API keys, paths) |
| `backend/database.py` | CREATE | SQLAlchemy engine + session |
| `backend/requirements.txt` | CREATE | FastAPI, Uvicorn, SQLAlchemy, Pydantic, NumPy |
| `backend/ruff.toml` | CREATE | Ruff linter config |
| `backend/tests/conftest.py` | CREATE | Pytest fixtures |
| `frontend/package.json` | CREATE | Electron + React + TypeScript + Vite |
| `frontend/electron-main.js` | CREATE | Electron main process |
| `frontend/tsconfig.json` | CREATE | TypeScript config |
| `frontend/vite.config.ts` | CREATE | Vite dev + Electron build config |
| `frontend/src/main.tsx` | CREATE | React entry point |
| `frontend/src/App.tsx` | CREATE | Basic component: fetch `/health` from backend |
| `frontend/src/services/api.ts` | CREATE | Axios client for backend API |
| `frontend/eslint.config.js` | CREATE | ESLint config |
| `.github/workflows/ci.yml` | CREATE | CI: lint + test on push/PR |
| `README.md` | CREATE | Getting started guide |

### Database Changes
- `strategies` table (id, name, odds_american, win_probability, bankroll, bet_size, bet_size_type, num_bets, num_simulations, strategy_type, created_at, updated_at)
- `simulation_runs` table (id, strategy_id, seed, created_at)
- `simulation_results` table (id, simulation_run_id, final_bankroll, is_profitable, created_at)

### Backend Tasks
1. Create FastAPI app with CORS middleware
2. Configure SQLite with SQLAlchemy, auto-create tables on startup
3. Implement `/health` endpoint
4. Set up `ruff` for linting, `pytest` for testing
5. Create `requirements.txt` with pinned versions
6. Create `.env.example` with API_KEY placeholder

### Frontend Tasks
1. Set up Electron + Vite + React + TypeScript template
2. Configure main process to launch browser window pointing to Vite dev server
3. Create API service that calls `http://localhost:8000/health`
4. Display connection status in the UI

### Tests
- `GET /health` returns 200 with `{"status": "ok"}`
- SQLite database file is created on startup
- Electron window launches without errors
- Frontend can fetch `/health` and display the response

### Verification Checklist
- [ ] `npm run dev` starts both backend and Electron
- [ ] FastAPI responds to `/health`
- [ ] SQLite database file exists
- [ ] CI passes on push

### Definition of Done
All deliverables created, all tests pass, CI is green, developer can run `npm run dev` and see a working window with a health check status.

### Out of Scope
- Simulation logic (Sprint 2)
- Strategy CRUD UI (Sprint 5)
- Any actual betting features

### Next Sprint Dependencies
- Backend must be running for frontend to connect to it
- Database schema must exist before Sprint 1 expands it

---

## Sprint 1 — Database Schema

### Purpose
Design and implement the complete database schema with all tables, indexes, and relationships. This is the single source of truth for all data in the application.

### Goal
All 16 database tables are defined as SQLAlchemy models, migrations run cleanly, and the database auto-creates on startup. Every table has proper indexes, foreign key relationships, and documentation.

### Why Now
GPT flagged the database as "my biggest request" — the schema needs to be fully designed before any CRUD or API work. Doing this as a standalone sprint ensures consistency across all future sprints. No other sprint touches data persistence, so this is a clean foundation to build on.

### Background
The application needs 16 tables covering: teams, games, odds (raw + normalized), injuries (raw + normalized), strategies, simulation runs and results, system play results, ML models, model predictions, backtest results, model evaluations, portfolios, and portfolio items. Each table must have proper indexing for query performance.

### Deliverables
- All 16 SQLAlchemy models defined with proper relationships
- Alembic migration setup
- Database initialization script
- Table documentation (purpose, columns, indexes, relationships)

### Acceptance Criteria
- [ ] Code committed and lint passes
- [ ] `pytest` passes (model creation tests)
- [ ] Database initializes all 16 tables on startup
- [ ] Foreign key relationships are enforced
- [ ] Indexes are created for all query-heavy columns
- [ ] Alembic migrations run cleanly

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/models/teams.py` | CREATE | Team model |
| `backend/models/games.py` | CREATE | Game model |
| `backend/models/odds.py` | CREATE | GameOdds, RawOdds models |
| `backend/models/injuries.py` | CREATE | Injuries, RawInjuries models |
| `backend/models/strategies.py` | CREATE | Strategy model |
| `backend/models/simulations.py` | CREATE | SimulationRun, SimulationResult models |
| `backend/models/system_plays.py` | CREATE | SystemPlayResult model |
| `backend/models/ml_models.py` | CREATE | MlModel, ModelPrediction, ModelEvaluation, BacktestResult models |
| `backend/models/portfolios.py` | CREATE | Portfolio, PortfolioItem models |
| `backend/migrations/` | CREATE | Alembic config + migration scripts |
| `backend/tests/test_models.py` | CREATE | Test all model instantiation + relationships |

### Database Changes
Full schema as documented in Technical Specification §8. All 16 tables with proper FKs, indexes, and constraints.

### Backend Tasks
1. Create all 16 SQLAlchemy model files with relationships
2. Set up Alembic for migrations
3. Generate initial migration script
4. Add indexes for all query-heavy columns (game_time, sport, model_id, created_at, etc.)
5. Write model unit tests

### Frontend Tasks
None

### Tests
- All 16 tables can be created
- Foreign key relationships work (strategy_id links to strategies, etc.)
- Indexes are present
- Alembic migration applies cleanly to empty database

### Verification Checklist
- [ ] `npm run dev` → server starts, DB has 16 tables
- [ ] `ruff check backend/models/` passes
- [ ] `pytest backend/tests/test_models.py` passes
- [ ] SQLite file has all tables with correct columns

### Definition of Done
All 16 tables defined, migrations work, tests pass, DB auto-creates on startup.

### Out of Scope
- CRUD operations (Sprint 4)
- API endpoints (Sprint 5)
- Any simulation logic

### Next Sprint Dependencies
- Sprint 2 needs database.py + models to be importable
- Sprint 4 needs models for CRUD operations

---

## Sprint 2 — Monte Carlo Core

### Purpose
Implement the Monte Carlo simulation engine in pure Python. This is the mathematical heart of the entire application.

### Goal
A pure-Python simulation module that can run a single simulation series and return final bankroll. Unit-tested, deterministic with seeded RNG. No API, no database — just math.

### Why Now
GPT specifically wanted Monte Carlo Core split from EV/Bankroll. These are distinct concerns: the core loop (simulating wins/losses) vs. the analysis (EV, drawdowns, Kelly). Keeping them separate means each is independently testable and reusable across all downstream features (System Plays, Parlay, Backtesting).

### Background
Each simulation run starts with a bankroll, then for each bet, rolls a random number against the win probability. If the roll succeeds, bankroll increases by profit; if not, bankroll decreases by the stake. Tracks the full trajectory for drawdown calculation.

### Deliverables
- Odds conversion utilities (American → Decimal → Implied Probability)
- `simulate_once()` — single simulation run returning bankroll trajectory
- `simulate_batch()` — runs 1,000–100,000 independent simulations
- `kelly_criterion()` — calculates optimal bet fraction
- NumPy-based RNG for performance

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers odds conversion + simulation edge cases
- [ ] 1,000 simulations × 100 bets completes in < 500ms
- [ ] Results are deterministic with same seed
- [ ] Kelly calculation matches formula: (bp - q) / b

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/simulation/__init__.py` | CREATE | Package init |
| `backend/simulation/odds.py` | CREATE | OddsConversion class |
| `backend/simulation/monte_carlo.py` | CREATE | simulate_once(), simulate_batch() |
| `backend/simulation/kelly.py` | CREATE | kelly_criterion(), half_kelly() |
| `backend/simulation/tests/conftest.py` | CREATE | RNG fixtures |
| `backend/simulation/tests/test_odds.py` | CREATE | Odds conversion tests |
| `backend/simulation/tests/test_monte_carlo.py` | CREATE | Simulation tests with known seeds |
| `backend/simulation/tests/test_kelly.py` | CREATE | Kelly criteria tests |

### Database Changes
None (pure logic)

### Backend Tasks
1. Implement `OddsConversion` class with static methods
2. Implement `simulate_once()` — single bet series, returns trajectory
3. Implement `simulate_batch()` — batch of simulations, returns list of trajectories
4. Implement `kelly_criterion()` and `half_kelly()`
5. All functions accept optional `seed` for deterministic testing

### Frontend Tasks
None

### Tests
- Odds: -110 → implied probability = 52.38%, +150 → decimal 2.50 → implied prob 40%
- Single simulation: with seed, known inputs produce known output
- Batch simulation: 1000 runs with 55% true prob at -110 → ~55% profitable runs
- Kelly: at -110 (decimal 1.909) with 55% win prob → kelly fraction ≈ 4.5%
- Performance: 1000 sims × 100 bets < 500ms

### Verification Checklist
- [ ] `ruff check backend/simulation/` passes
- [ ] `pytest backend/simulation/tests/` passes
- [ ] `simulate_batch(1000)` completes in < 500ms
- [ ] Same seed → same results

### Definition of Done
Simulation engine fully implemented, all unit tests pass, results match mathematical expectations.

### Out of Scope
- API endpoints (Sprint 5)
- Metrics calculation (Sprint 3)
- Frontend integration (Sprint 6)

### Next Sprint Dependencies
- Sprint 3 needs `simulate_batch()` to calculate metrics

---

## Sprint 3 — EV & Bankroll Calculations

### Purpose
Implement the metrics calculation and bankroll strategy logic. This transforms raw simulation trajectories into actionable metrics (EV, risk of ruin, max drawdown) and supports multiple betting strategies (flat, percentage, Kelly).

### Goal
A metrics module that takes simulation trajectories and returns aggregated metrics (win %, EV, risk of ruin, max drawdown, distribution). A bankroll module that implements flat, percentage, Kelly, and half-Kelly stake calculations.

### Why Now
The Monte Carlo engine (Sprint 2) produces raw trajectories — arrays of bankroll values. Without metrics, those trajectories are useless. GPT wanted this split from the core simulation because it's a distinct analytical concern. Separating metrics also means the simulation engine stays pure (no statistics) and metrics can be tested independently.

### Background
Metrics include: win percentage (fraction of profitable runs), expected value (average profit per bet), risk of ruin (fraction of runs that hit $0), max drawdown (worst peak-to-trough decline), and distribution statistics (mean, median, std dev, percentiles). Bankroll strategies determine how much to bet each round.

### Deliverables
- `calculate_metrics()` — full metrics from trajectories
- `calculate_stake()` — stake calculation for each bankroll strategy
- `risk_of_ruin()` — percentage of simulations that go bust
- `max_drawdown()` — worst drawdown per simulation
- Distribution calculation (histogram bins, percentiles)
- Kelly fraction calculation (refactor from Sprint 2)

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers all metric calculations
- [ ] EV calculation matches formula: p × profit - (1-p) × stake
- [ ] Risk of ruin = % of runs where bankroll hits $0
- [ ] Kelly strategy stake calculation is correct

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/simulation/metrics.py` | CREATE | calculate_metrics(), risk_of_ruin(), max_drawdown() |
| `backend/simulation/distribution.py` | CREATE | Percentile calculation, histogram binning |
| `backend/simulation/bankroll.py` | CREATE | calculate_stake() for each strategy |
| `backend/simulation/kelly.py` | MODIFY | Add calculate_kelly_fraction() if not done in Sprint 2 |
| `backend/simulation/tests/test_metrics.py` | CREATE | Metrics tests |
| `backend/simulation/tests/test_bankroll.py` | CREATE | Bankroll strategy tests |
| `backend/simulation/tests/test_distribution.py` | CREATE | Distribution tests |

### Database Changes
None

### Backend Tasks
1. Implement `calculate_metrics(trajectories, starting_bankroll)` — full metrics calculation
2. Implement `calculate_stake(strategy, bankroll, bet_size, kelly_fraction)` — stake per strategy
3. Implement `max_drawdown(trajectory)` — peak-to-trough analysis
4. Implement `distribution_stats(final_bankrolls, num_bins)` — histogram + percentiles
5. Unit test all functions

### Frontend Tasks
None

### Tests
- EV = win_prob × profit_per_win - (1-win_prob) × stake_per_loss
- Risk of ruin = runs where final bankroll ≤ 0
- Max drawdown = max peak-to-trough decline
- Distribution: histogram bins sum to total simulation count
- Stake calculation correct for each strategy type

### Verification Checklist
- [ ] `pytest backend/simulation/tests/` passes
- [ ] Metrics match manual calculation
- [ ] Stake calculation correct for all 4 strategies

### Definition of Done
Metrics module fully implemented and tested. Bankroll strategies work correctly.

### Out of Scope
- API endpoints (Sprint 5)
- Frontend integration (Sprint 6)
- System Plays calibration (Sprint 10)

### Next Sprint Dependencies
- Sprint 5 needs metrics for API response
- Sprint 6 needs metrics for UI display

---

## Sprint 4 — Repository Layer

### Purpose
Implement the data access layer (CRUD operations) for all database tables. This is the boundary between business logic and persistence.

### Goal
Complete CRUD operations for all 16 tables, accessible via a clean repository interface. Every read, write, update, and delete operation is tested.

### Why Now
GPT's plan puts Repository Layer (Sprint 2) right after Database Schema (Sprint 1). This creates a clean separation: Sprint 1 designs the schema, Sprint 4 provides the access layer, Sprint 5 builds the API on top. No API endpoint can be built without CRUD operations, so this must come first.

### Background
The repository layer abstracts SQLAlchemy queries behind clean functions. Each CRUD operation returns Pydantic models, not raw SQLAlchemy objects. This separation keeps business logic testable without a database.

### Deliverables
- CRUD for strategies (save, load, list, update, delete)
- CRUD for simulation runs + results (store batch results)
- CRUD for games + odds (future use)
- CRUD for ML models + predictions (future use)
- CRUD for system play results (Sprint 10 use)
- CRUD for portfolios + portfolio items (Sprint 14 use)
- CRUD for backtest results (Sprint 12 use)

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers all CRUD operations
- [ ] Each CRUD function returns Pydantic model, not SQLAlchemy object
- [ ] Foreign key relationships work in queries
- [ ] Database transactions are atomic

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/crud/__init__.py` | MODIFY | Export all CRUD modules |
| `backend/crud/strategy.py` | CREATE | Strategy CRUD |
| `backend/crud/simulation.py` | CREATE | SimulationRun + Results CRUD |
| `backend/crud/odds.py` | CREATE | Games + odds CRUD |
| `backend/crud/ml_models.py` | CREATE | ML models + predictions CRUD |
| `backend/crud/system_plays.py` | CREATE | System play results CRUD |
| `backend/crud/portfolios.py` | CREATE | Portfolios + items CRUD |
| `backend/crud/backtest.py` | CREATE | Backtest results CRUD |
| `backend/crud/tests/test_strategy.py` | CREATE | Strategy CRUD tests |
| `backend/crud/tests/test_simulation.py` | CREATE | Simulation CRUD tests |

### Database Changes
None (schema already exists from Sprint 1)

### Backend Tasks
1. Implement `strategy.py` — save_strategy, get_strategy, list_strategies, update_strategy, delete_strategy
2. Implement `simulation.py` — save_simulation_run, save_simulation_results, get_run_results
3. Implement `odds.py` — save_game, save_game_odds, get_games_by_sport
4. Implement `ml_models.py` — save_model, get_active_model, save_prediction
5. Implement `system_plays.py` — save_calibration_result
6. Implement `portfolios.py` — save_portfolio, get_portfolio
7. Implement `backtest.py` — save_backtest_result, get_model_backtests
8. Write integration tests with SQLite in-memory DB

### Frontend Tasks
None

### Tests
- Each CRUD function returns correct Pydantic model
- Foreign key constraints enforced
- Bulk insert of simulation results works (1000 rows)
- Queries with joins work (strategy → simulation_runs → results)
- Database rollback works on error

### Verification Checklist
- [ ] `pytest backend/crud/tests/` passes
- [ ] All 16 tables have CRUD functions
- [ ] No raw SQLAlchemy objects leak to API layer

### Definition of Done
All CRUD operations implemented, tested, and returning Pydantic models.

### Out of Scope
- API endpoints (Sprint 5)
- Frontend integration (Sprint 6)

### Next Sprint Dependencies
- Sprint 5 needs CRUD functions to implement API endpoints

---

## Sprint 5 — Backend API

### Purpose
Expose the simulation engine and data through a REST API. This is the contract the frontend consumes.

### Goal
All API endpoints are implemented, documented via OpenAPI, and tested. Frontend can call every endpoint it needs for MVP.

### Why Now
The simulation engine (Sprint 2), metrics (Sprint 3), and CRUD layer (Sprint 4) are all ready. The API is the bridge between them and the frontend. No frontend feature can be built without these endpoints.

### Background
API endpoints: POST /api/simulate (run simulation), CRUD for /api/strategies, POST /api/system-plays (calibration), POST /api/parlay/simulate. Each endpoint validates input via Pydantic, calls the appropriate service, and returns structured JSON.

### Deliverables
- POST `/api/simulate` — run Monte Carlo simulation, return metrics + charts data
- GET/POST/PUT/DELETE `/api/strategies` — full CRUD
- POST `/api/simulate/{strategy_id}` — run sim using saved strategy
- POST `/api/system-plays` — model calibration endpoint
- POST `/api/parlay/simulate` — parlay simulation
- GET `/api/health` — health check
- OpenAPI schema auto-generated at `/docs`

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers all endpoint integration tests
- [ ] OpenAPI schema shows all endpoints
- [ ] CORS configured for Electron renderer
- [ ] 422 returned for invalid input
- [ ] 404 returned for non-existent resources

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/api/__init__.py` | CREATE | Router registration |
| `backend/api/deps.py` | CREATE | DB session dependency |
| `backend/api/simulation.py` | CREATE | /api/simulate endpoints |
| `backend/api/strategies.py` | CREATE | /api/strategies CRUD |
| `backend/api/system_plays.py` | CREATE | /api/system-plays |
| `backend/api/parlay.py` | CREATE | /api/parlay/simulate |
| `backend/schemas/simulation.py` | CREATE | SimulationRequest, SimulationResponse |
| `backend/schemas/strategy.py` | CREATE | StrategyCreate, StrategyRead, StrategyUpdate |
| `backend/schemas/system_plays.py` | CREATE | CalibrationReport |
| `backend/schemas/parlay.py` | CREATE | ParlayRequest, ParlayResponse |
| `backend/tests/test_api.py` | CREATE | Integration tests for all endpoints |

### Database Changes
None (schema from Sprint 1, CRUD from Sprint 4)

### Backend Tasks
1. Implement API router with all endpoints
2. Wire up CRUD layer to API handlers
3. Wire up simulation engine to /api/simulate
4. Add CORS middleware for Electron renderer
5. Validate all inputs with Pydantic schemas
6. Add error handling (422, 404, 500)
7. Generate API contract table (Endpoint | Input | Output | Used By)

### Frontend Tasks
None

### Tests
- POST `/api/simulate` returns 200 with correct metrics
- POST `/api/simulate` with invalid input returns 422
- GET `/api/strategies` returns 200 with list
- POST/GET/PUT/DELETE on `/api/strategies/{id}` work correctly
- POST `/api/system-plays` returns calibration report
- POST `/api/parlay/simulate` returns combined probability + metrics
- `/docs` shows OpenAPI UI

### Verification Checklist
- [ ] All endpoints respond with correct status codes
- [ ] Simulation results match direct engine output
- [ ] CORS allows requests from Electron renderer (localhost:5173)
- [ ] `/docs` renders OpenAPI UI

### Definition of Done
All API endpoints implemented, tested, and documented. Frontend can call every endpoint needed for MVP.

### Out of Scope
- Frontend UI (Sprint 6)
- Live odds endpoints (Sprint 9)
- ML prediction endpoints (Sprint 13)

### Next Sprint Dependencies
- Sprint 6 needs /api/simulate and /api/health
- Sprint 8 needs /api/strategies CRUD

---

## Sprint 6 — Dashboard Framework

### Purpose
Build the main UI: the Simulation Workspace where users input parameters and see results. This is the primary entry point.

### Goal
A functional simulation workspace where a user can fill in odds, win probability, bankroll, bet size, number of bets, and number of simulations, click "Run Simulation," and see the basic results (win %, EV, risk of ruin).

### Why Now
The backend API is ready (Sprint 5). Without a UI, the app is just a library. The simulation workspace is the primary user touchpoint — everything else (charts, strategies, System Plays) builds on this page.

### Background
The workspace has two columns: input form on the left, results display on the right. The form validates inputs and calls POST `/api/simulate`. Results show metric cards. Navigation allows switching to other pages (Strategies, System Plays, etc.).

### Deliverables
- Responsive two-column layout (form + results)
- Input form: odds (American), win probability, bankroll, bet size, strategy type, num bets, num simulations
- "Run Simulation" button with loading state
- Results: win %, avg ending bankroll, risk of ruin, EV
- Error handling (display validation errors)
- Navigation bar (links to all pages)
- Dark mode theme (CSS variables, no light mode toggle)
- Onboarding modal (first-run tutorial walkthrough)
- Settings page (defaults, API keys, storage location)

### Acceptance Criteria
- [ ] `npm run lint` passes on frontend
- [ ] `vitest` covers form validation + API calls
- [ ] Form validates all inputs before submit
- [ ] "Run Simulation" calls API and displays results
- [ ] Loading spinner shows during API call
- [ ] Error messages are user-friendly

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `frontend/src/App.tsx` | MODIFY | Root component + React Router |
| `frontend/src/pages/SimulationWorkspace.tsx` | CREATE | Main workspace page |
| `frontend/src/components/SimulationForm.tsx` | CREATE | Input form with validation |
| `frontend/src/components/ResultsDisplay.tsx` | CREATE | Metric cards display |
| `frontend/src/components/Navigation.tsx` | CREATE | Dark-mode nav bar with links |
| `frontend/src/components/OnboardingModal.tsx` | CREATE | First-run tutorial walkthrough |
| `frontend/src/pages/Settings.tsx` | CREATE | Settings page (defaults, API keys, storage) |
| `frontend/src/types/simulation.ts` | CREATE | TypeScript types |
| `frontend/src/hooks/useSimulation.ts` | CREATE | React hook for sim state |
| `frontend/src/__tests__/SimulationForm.test.tsx` | CREATE | Form validation tests |
| `frontend/src/__tests__/ResultsDisplay.test.tsx` | CREATE | Results display tests |

### Database Changes
None

### Backend Tasks
- Ensure `/api/simulate` response schema matches frontend types
- Add Swagger examples to API docs

### Frontend Tasks
1. Set up React Router for page navigation
2. Create TypeScript types matching backend schemas
3. Build `SimulationForm` with validation
4. Build `ResultsDisplay` with metric cards
5. Create `useSimulation` hook for state management
6. Wire up API call to POST `/api/simulate`
7. Build `Navigation` component (dark mode themed)
8. Build `OnboardingModal` (first-run tutorial)
9. Build `Settings` page with default preferences
10. Apply dark mode CSS variables throughout

### Tests
- Form validates: odds can be negative, probability is 0–100%, bankroll > 0
- "Run Simulation" calls API with correct payload
- Results display shows win %, avg bankroll, risk of ruin
- Loading state shows spinner
- API errors are displayed to user
- Implied probability is calculated and shown
- Dark mode theme applies correctly (no flash of white)
- Onboarding modal appears on first launch
- Settings page saves default preferences to SQLite

### Verification Checklist
- [ ] `npm run dev` launches Electron with workspace page
- [ ] Form inputs validate correctly
- [ ] Simulation runs and returns results
- [ ] Key metrics are displayed
- [ ] Error states are handled
- [ ] Navigation works to all pages
- [ ] Dark mode is the only theme (no light mode)
- [ ] Onboarding appears on first run, suppressed on subsequent runs
- [ ] Settings page saves and persists preferences

### Verification Checklist
- [ ] `npm run dev` launches Electron with workspace page
- [ ] Form inputs validate correctly
- [ ] Simulation runs and returns results
- [ ] Key metrics are displayed
- [ ] Error states are handled
- [ ] Navigation works to other pages

### Definition of Done
User can fill in bet parameters, run a simulation, and see basic results. Navigation works to all pages. Form validation prevents invalid inputs. Dark mode is the only theme. Onboarding modal appears on first run. Settings page works.

### Out of Scope
- Charts (Sprint 7)
- Strategy saving (Sprint 8)
- System Plays (Sprint 10)

### Next Sprint Dependencies
- Sprint 7 needs simulation results data for charts
- Sprint 7 needs dark mode CSS variables
- Sprint 8 needs strategy CRUD endpoints

---

## Sprint 7 — Visualization & Charting

### Purpose
Add charts and graphs to visualize simulation results. Numbers are useful, but visual representation of bankroll trajectories and distributions makes the risk/variance story clear.

### Goal
Two charts that render from simulation data: a bankroll trajectory chart (showing median path + best/worst percentiles) and a bankroll distribution histogram (showing the spread of final bankrolls across all simulation runs).

### Why Now
The workspace (Sprint 6) shows raw numbers. Charts are what make the risk story visceral — users need to *see* the distribution of outcomes and the range of possible bankroll paths. This is the educational core of the product.

### Background
The API returns trajectory percentiles (median, p10, p90, min, max) and distribution bins. We use Recharts to render a multi-line chart for trajectories and a bar chart for the histogram.

### Deliverables
- Bankroll trajectory line chart (median + percentile bands)
- Bankroll distribution histogram
- Metrics summary table (max drawdown, worst case, best case, EV)
- Interactive hover tooltips
- Scenario library dropdown (pre-built betting scenarios for instant simulation)
- Dark mode styling for all chart components

### Acceptance Criteria
- [ ] `vitest` passes for all chart components
- [ ] Charts render correctly with data
- [ ] No-data state shows placeholder
- [ ] Hover tooltips show correct values
- [ ] Charts are responsive

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `frontend/src/components/BankrollChart.tsx` | CREATE | Line chart using Recharts |
| `frontend/src/components/DistributionChart.tsx` | CREATE | Histogram using Recharts |
| `frontend/src/components/MetricsTable.tsx` | CREATE | Table with all metrics |
| `frontend/src/components/SimulationResults.tsx` | CREATE | Container for all result displays |
| `frontend/src/utils/chartData.ts` | CREATE | Transform API response → chart data |
| `frontend/src/components/ScenarioLibrary.tsx` | CREATE | Pre-built betting scenarios dropdown |
| `frontend/src/data/scenarios.ts` | CREATE | Scenario definitions (NFL, MMA, parlays, etc.) |
| `frontend/package.json` | MODIFY | Add `recharts` dependency |
| `frontend/src/__tests__/BankrollChart.test.tsx` | CREATE | Chart rendering tests |
| `frontend/src/__tests__/DistributionChart.test.tsx` | CREATE | Histogram tests |

### Database Changes
None

### Backend Tasks
- Ensure simulation response includes percentile trajectories + distribution bins
- Add `charts` field to response if not present

### Frontend Tasks
1. Install Recharts
2. Build `BankrollChart` — multi-line: median (primary), p10/p90 (band), min/max (faint)
3. Build `DistributionChart` — histogram of final bankrolls
4. Build `MetricsTable` — max drawdown, worst case, best case, std dev, EV
5. Create `SimulationResults` container
6. Add chart data transformation utilities
7. Build `ScenarioLibrary` dropdown with 4 pre-built scenarios
8. Apply dark mode styling to all chart components

### Tests
- Charts render without errors when data is present
- No-data state shows placeholder message
- Hover tooltips show correct values
- Trajectory data transforms correctly to chart format
- Distribution bins sum to total simulation count
- Scenario library loads pre-built scenarios
- Chart colors work in dark mode

### Verification Checklist
- [ ] Bankroll trajectory chart shows median + percentiles
- [ ] Distribution histogram renders correctly
- [ ] Metrics table shows all values from API
- [ ] Charts are responsive on different screen sizes
- [ ] Scenario library dropdown works
- [ ] Charts are styled for dark mode

### Definition of Done
After running a simulation, user sees: bankroll trajectory chart, distribution histogram, and metrics table. All visualizations are clear and responsive. Scenario library dropdown works. Everything styled in dark mode.

### Out of Scope
- Strategy saving (Sprint 8)
- System Plays (Sprint 10)

### Next Sprint Dependencies
- Sprint 8 needs strategy CRUD endpoints

---

## Sprint 8 — Strategy Management

### Purpose
Allow users to save, load, compare, and manage their betting strategies. Instead of re-entering parameters each time, users can save a strategy and recall it.

### Goal
A strategies page where users can see their saved strategies as cards, click to run a simulation, edit or delete them. From the workspace, a "Save Strategy" button persists the current form state.

### Why Now
Users are running simulations (Sprinds 6–7) and starting to form strategies. Without the ability to save them, they'll re-type parameters every time — a major friction point. Saving strategies is the bridge between "I want to explore this bet" and "I want to build a repeatable process."

### Background
The API has strategy CRUD endpoints (Sprint 5). The frontend needs UI to interact with them and display saved strategies.

### Deliverables
- Strategies list page (grid of strategy cards)
- "Save Strategy" button on workspace (saves current form values)
- Strategy card: shows key params (odds, win %, bankroll, bet size)
- Edit strategy form (prefilled with saved values)
- Delete with confirmation
- Run simulation from a saved strategy
- Export results to CSV
- Simulation History page (table of past runs with filter/sort)
- Re-run simulation from history

### Acceptance Criteria
- [ ] `vitest` covers strategy CRUD hooks
- [ ] Strategies can be saved from workspace
- [ ] Strategies page lists all saved strategies
- [ ] Edit/delete work correctly
- [ ] Running from saved strategy uses correct params
- [ ] CSV export produces valid data

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `frontend/src/pages/Strategies.tsx` | CREATE | List page for strategies |
| `frontend/src/components/StrategyCard.tsx` | CREATE | Card with strategy summary + actions |
| `frontend/src/components/StrategyEditor.tsx` | CREATE | Form to edit strategy (reusable) |
| `frontend/src/components/ExportButton.tsx` | CREATE | Export simulation results as CSV |
| `frontend/src/services/strategiesApi.ts` | CREATE | Strategy API client |
| `frontend/src/hooks/useStrategies.ts` | CREATE | React hook for strategy CRUD |
| `frontend/src/utils/csvExport.ts` | CREATE | Convert results to CSV |
| `frontend/src/types/strategy.ts` | CREATE | Strategy types |
| `frontend/src/__tests__/StrategyCard.test.tsx` | CREATE | Component tests |
| `frontend/src/__tests__/useStrategies.test.ts` | CREATE | Hook tests |
| `frontend/src/pages/ResultsHistory.tsx` | CREATE | History browser page |
| `frontend/src/components/ResultsHistoryTable.tsx` | CREATE | Table of past simulations |
| `frontend/src/services/historyApi.ts` | CREATE | History API client |

### Database Changes
None (schema from Sprint 1, CRUD from Sprint 4)

### Backend Tasks
- Verify strategy CRUD endpoints work correctly
- Add response model for strategy comparison

### Frontend Tasks
1. Create `strategiesApi.ts` — get/save/update/delete
2. Build `Strategies` page — fetch + display strategy cards
3. Build `StrategyCard` — shows params + Run/Edit/Delete buttons
4. Build `StrategyEditor` — reusable form for create/edit
5. Add "Save Strategy" to workspace
6. Create `ExportButton` — CSV export
7. Add CSV export utility
8. Build `ResultsHistory` page — table of past simulations
9. Build `ResultsHistoryTable` — filter/sort past results
10. Build `historyApi.ts` — fetch simulation history

### Tests
- Save strategy from workspace persists to backend
- Strategies list loads and displays correctly
- Edit strategy updates backend and reflects changes
- Delete strategy removes from list with confirmation
- Export produces valid CSV with correct columns
- Running from saved strategy uses correct params
- Simulation history table shows past runs
- History can be filtered by date/sport/strategy
- History re-run uses saved params

### Verification Checklist
- [ ] User can save current workspace params as a strategy
- [ ] Strategies page lists all saved strategies
- [ ] User can edit or delete any strategy
- [ ] User can run a simulation from a saved strategy
- [ ] Results can be exported as CSV
- [ ] Simulation history is displayed
- [ ] History can be filtered
- [ ] History re-run works

### Definition of Done
Users can save, view, edit, delete, and run simulations from saved strategies. Results can be exported as CSV.

### Out of Scope
- System Plays (Sprint 10)
- Parlay Simulator (Sprint 11)

### Next Sprint Dependencies
- Sprint 10 needs strategy persistence for calibration results

---

## Sprint 9 — Data Collection & Feature Engineering

### Purpose
Set up the data collection pipeline. Integrate with TheOddsAPI to fetch live odds, normalize them, and build the feature schema for future ML models.

### Goal
A scheduled service that fetches odds from TheOddsAPI, normalizes them into canonical format, stores them in SQLite, and provides a feature extraction pipeline ready for ML model training.

### Why Now
The app is fully functional with manual input (Sprints 0–8). But entering odds manually is the last bit of friction. Live odds make the app feel professional and set up the ML model. GPT split this into Collectors + Normalization + Features — three distinct concerns. We combine Normalization + Features into one sprint since they're tightly coupled (features are derived from normalized data).

### Background
TheOddsAPI provides a free tier (25 req/day) perfect for development. The collector fetches odds, the normalizer maps them to canonical format (American odds, implied probability), and the feature pipeline extracts model-ready vectors.

### Deliverables
- TheOddsAPI client (collector)
- Validation layer (JSON schema validation, retry logic, duplicate detection)
- Normalizer (provider-specific → canonical)
- Raw tables (`raw_odds`, `raw_injuries`)
- Normalized tables (`games`, `game_odds`, `teams`, `injuries`)
- Feature schema (30+ features defined)
- `extract_features()` function
- `/api/odds/games` endpoint
- Live odds selector in workspace UI

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers collector + normalizer
- [ ] Data fetched and stored in raw tables
- [ ] Normalized data available via API
- [ ] Feature extraction produces correct shape
- [ ] Live odds can be selected in workspace

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/services/__init__.py` | MODIFY | Export services |
| `backend/services/odds_api.py` | CREATE | TheOddsAPI client |
| `backend/services/scheduler.py` | CREATE | Background task scheduler |
| `backend/services/cache.py` | CREATE | In-memory odds cache |
| `backend/services/collector.py` | CREATE | BaseCollector interface + TheOddsApiCollector |
| `backend/services/normalizer.py` | CREATE | Normalize raw data → canonical |
| `backend/services/validator.py` | CREATE | JSON schema validation |
| `backend/ml/features/schema.py` | CREATE | Feature definitions |
| `backend/ml/features/engineering.py` | CREATE | extract_features() |
| `backend/api/odds.py` | CREATE | /api/odds/* endpoints |
| `backend/schemas/odds.py` | CREATE | Odds Pydantic schemas |
| `backend/services/tests/test_odds_api.py` | CREATE | API client tests |
| `backend/services/tests/test_normalizer.py` | CREATE | Normalizer tests |
| `backend/ml/features/tests/test_engineering.py` | CREATE | Feature extraction tests |

### Database Changes
- `raw_odds` table (provider, provider_game_id, sport, teams, market_type, odds, timestamp, raw_json)
- `raw_injuries` table (provider, player, team, injury_type, severity, reported_at, raw_json)
- `teams` table (id, name, sport, league, city, abbreviation)
- `games` table (id, sport, teams, scores, game_time, status, season, week)
- `game_odds` table (game_id, sportsbook, market_type, outcome, odds, timestamp)
- `injuries` table (player_name, team_id, sport, injury_type, severity, reported_at)

### Backend Tasks
1. Implement `BaseCollector` ABC with `fetch()` and `get_provider_name()`
2. Implement `TheOddsApiCollector` — fetch games + odds from TheOddsAPI
3. Implement `Validator` — JSON schema validation, retry logic, duplicate detection
4. Implement `Normalizer` — map provider data to canonical format
5. Implement `extract_features()` — transform raw + normalized → feature vector
6. Create `/api/odds/games?sport=nba` endpoint
7. Set up `SchedulerService` for periodic collection
8. Configure in-memory cache with stale threshold (2 hours)

### Frontend Tasks
1. Add "Use Live Odds" toggle to SimulationForm
2. Create `OddsSelector` component — dropdown of live games
3. Create `LiveOddsBadge` component — shows "Live" or "Stale"
4. Display implied probability when live odds selected

### Tests
- TheOddsAPI client parses response correctly
- Normalizer maps provider data to canonical format
- Duplicate detection works (same game_id + timestamp → skip)
- `/api/odds/games` returns list of games
- Live odds can be selected and used in simulation
- Implied probability is calculated from live odds
- Stale data indicator works (odds older than 2 hours = stale)

### Verification Checklist
- [ ] TheOddsAPI key configured (in .env)
- [ ] Odds are fetched and stored on startup
- [ ] Games list endpoint works
- [ ] User can select live odds in workspace
- [ ] Implied probability is displayed

### Definition of Done
The app can fetch live odds from TheOddsAPI, store them, and the user can select live odds in the simulation workspace. Implied probability is calculated and displayed.

### Out of Scope
- ML model training (Sprint 13)
- Real-time odds updates (future)
- Injury data integration (beyond stub)

### Next Sprint Dependencies
- Sprint 13 needs data pipeline for model training

---

## Sprint 10 — System Plays Engine

### Purpose
Build the System Plays Engine — the core differentiator. This is the mechanism by which the app validates whether a probability model (user-input or ML) is actually calibrated.

### Goal
A "System Plays" page where users input their estimated probability for a bet, run 1000+ simulations, and see the gap between their stated probability and the simulation reality. The system also validates itself.

### Why Now
GPT listed System Plays as the key differentiator. We have the simulation engine (Sprint 2), metrics (Sprint 3), API (Sprint 5), UI framework (Sprint 6), charts (Sprint 7), strategy management (Sprint 8), and data pipeline (Sprint 9). All building blocks are ready. Now we deliver the feature that no other betting tool has: model calibration through simulation.

### Background
> "The system tells us through 1000 simulations that there's 70% X wins, well it would play that chance and see for itself"

The System Plays Engine runs Monte Carlo simulations with a stated probability and compares the actual win rate to the stated probability. The gap is the calibration error — telling users if their model is overconfident, underconfident, or well-calibrated.

### Deliverables
- System Plays input: bet odds, user-stated win probability, bankroll, bet size
- Run 1,000–10,000 simulations
- Display: stated vs. actual win rate, calibration error, EV, risk of ruin
- Calibration report with confidence intervals
- Calibration chart (stated vs. actual bar chart)
- Educational recommendation text

### Acceptance Criteria
- [ ] Code committed and lint passes
- [ ] `pytest` covers calibration logic
- [ ] Stated vs. actual probability display is accurate
- [ ] Confidence intervals are correct
- [-code] Educational insight is provided
- [ ] Calibration chart renders correctly

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `frontend/src/pages/SystemPlays.tsx` | CREATE | System Plays main page |
| `frontend/src/components/CalibrationChart.tsx` | CREATE | Bar chart: stated vs. actual |
| `frontend/src/components/SystemPlaysResults.tsx` | CREATE | Full results display |
| `backend/simulation/calibration.py` | CREATE | `calibrate_model()` |
| `backend/api/system_plays.py` | CREATE | `/api/system-plays` endpoint |
| `backend/schemas/system_plays.py` | CREATE | CalibrationReport schema |
| `backend/simulation/tests/test_calibration.py` | CREATE | Calibration tests |

### Database Changes
- `system_play_results` table: id, simulation_run_id, stated_probability, actual_win_rate, calibration_error, calibration_status, confidence_interval_low, confidence_interval_high, recommendation, created_at

### Backend Tasks
1. Implement `calibrate_model(odds_decimal, win_prob, bankroll, bet_size, num_bets, num_simulations, seed)`
2. Implement `/api/system-plays` endpoint
3. Store system play results in database
4. Return calibration report with confidence intervals

### Frontend Tasks
1. Build `SystemPlays` page with input form
2. Build `CalibrationChart` — bar chart comparing stated vs. actual
3. Build `SystemPlaysResults` — full results including calibration error
4. Show confidence intervals and educational recommendations

### Tests
- System Plays returns correct calibration comparison
- Calibration chart shows correct data
- Stated vs. actual probability display is accurate
- Confidence intervals are correct (95% CI for binomial)
- Educational text appears for miscalibrated models

### Verification Checklist
- [ ] User inputs stated probability + bet params
- [ ] 1,000+ simulations run
- [ ] Actual win rate is compared to stated probability
- [ ] Calibration error + confidence interval is displayed
- [ ] Educational insight is provided

### Definition of Done
The System Plays Engine runs. Users can input probability estimates and see how well they're calibrated through simulation.

### Out of Scope
- ML model integration (Sprint 13)
- Historical system plays tracking (Sprint 12)

### Next Sprint Dependencies
- Sprint 11 needs simulation engine for variance calculation

---

## Sprint 11 — Parlay Simulator + Bankroll Comparison

### Purpose
Build the parlay simulator AND bankroll strategy comparison. These are both about "different ways to bet" and naturally complement each other.

### Goal
Parlay builder where users can combine 2–6 selections, see combined probability and EV, and simulate variance. Plus bankroll strategy toggle (Flat/Percentage/Kelly/Half-Kelly) with side-by-side comparison.

### Why Now
The core simulation is mature (Sprints 2–10). Parlays are the #1 way recreational bettors lose money — showing WHY is pure educational value. Bankroll strategy comparison is the #1 skill gap for bettors. Both use the same underlying engine but present different risk stories.

### Background
A parlay requires ALL selections to win. Combined probability = product of all probabilities. Combined payout = product of all decimal odds. EV = combined_prob × (combined_payout - 1) - (1 - combined_prob). The simulator shows that even with positive EV on each leg, parlays are usually negative EV due to the multiplication of probabilities.

### Deliverables
- Parlay builder: add/remove selections, input odds + probability for each
- Combined probability + payout calculation
- Parlay simulation (variance analysis)
- Bankroll strategy selector (Flat/Percentage/Kelly/Half-Kelly)
- Side-by-side strategy comparison (risk of ruin, avg growth)

### Acceptance Criteria
- [ ] Code committed and lint passes
- [ ] `vitest` covers parlay builder + strategy selector
- [ ] Parlay combined probability is correct (0.55³ = 0.166)
- [ ] Parlay payout calculation is correct
- [ ] Strategy comparison shows different risk/return profiles
- [ ] Kelly fraction is displayed and updates with input changes

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `frontend/src/pages/ParlaySimulator.tsx` | CREATE | Parlay builder + simulator |
| `frontend/src/components/ParlayBuilder.tsx` | CREATE | Selections list UI |
| `frontend/src/components/ParlayResults.tsx` | CREATE | Parlay simulation results |
| `frontend/src/components/BankrollStrategySelector.tsx` | CREATE | Flat/Percentage/Kelly/Half-Kelly toggle |
| `frontend/src/components/StrategyComparison.tsx` | CREATE | Side-by-side strategy results |
| `frontend/src/components/KellyCalculator.tsx` | CREATE | Live Kelly fraction display |
| `backend/simulation/parlay.py` | CREATE | `simulate_parlay()` |
| `backend/api/parlay.py` | CREATE | `/api/parlay/simulate` endpoint |
| `backend/schemas/parlay.py` | CREATE | ParlayRequest, ParlayResponse |

### Database Changes
- Add `bankroll_strategy` column to `strategies` table
- Add `kelly_fraction` column to `strategies` table

### Backend Tasks
1. Implement `simulate_parlay(selections, bankroll, bet_size, num_simulations)`
2. Implement `/api/parlay/simulate` endpoint
3. Calculate combined probability + payout
4. Return variance metrics for parlay vs. single bets

### Frontend Tasks
1. Build `ParlayBuilder` — add/remove/edit selections
2. Build `ParlayResults` — display combined probability, payout, EV
3. Build `BankrollStrategySelector` — radio toggle
4. Build `KellyCalculator` — show recommended fraction
5. Build `StrategyComparison` — table comparing strategies
6. Add strategy selector to SimulationForm
7. Add comparison display to SimulationResults

### Tests
- Parlay combined probability calculation is correct
- Parlay payout calculation is correct (decimal odds multiplied)
- Strategy comparison API returns results for all strategies
- Kelly fraction calculated correctly
- Warning triggers when bankroll drops below 50%

### Verification Checklist
- [ ] User can build a parlay (2–6 selections)
- [ ] Combined probability + payout calculated correctly
- [ ] Monte Carlo simulation runs
- [ ] User can toggle bankroll strategies
- [ ] Strategy comparison shows different risk/return profiles
- [ ] Kelly fraction is displayed and updates

### Definition of Done
Users can build parlays, simulate them, and see true risk vs. single bets. Bankroll strategy comparison works with Kelly auto-calculation.

### Out of Scope
- Live odds integration (Sprint 9)
- Portfolio construction (Sprint 14)

### Next Sprint Dependencies
- Sprint 12 needs simulation results for backtesting

---

## Sprint 12 — Backtesting Engine

### Purpose
Build the backtesting engine that validates models against historical game results. This feeds into model evaluation, calibration, and retraining decisions.

### Goal
A backtesting pipeline that takes historical predictions, matches them against actual game results, and produces accuracy, calibration, ROI, and Brier score metrics.

### Why Now
The System Plays Engine (Sprint 10) validates probability estimates against simulation. But for ML models, we need validation against REAL historical results. The Backtesting Engine is what closes the loop: Model trains → predicts → we compare to actual results → we evaluate → we decide to retrain. Without this, the ML pipeline (Sprint 13) has no feedback loop.

### Background
When a game ends, the Data Collection service stores the final score. The BacktestService then looks up any predictions made for that game, compares the predicted probability to the actual outcome, and records the result. Over time, these results feed into model_evaluations.

### Deliverables
- BacktestService: historical replay engine
- `backtest_results` table populated from predictions + actual outcomes
- Model evaluation: accuracy, calibration error, ROI, Brier score
- Analytics dashboard: historical performance trends
- Auto-triggered backtests when games complete

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers backtest logic
- [ ] Backtest results populate correctly
- [ ] Model evaluation metrics are accurate
- [ ] Analytics dashboard shows historical trends

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/ml/backtest.py` | CREATE | BacktestService |
| `backend/api/analytics.py` | CREATE | /api/analytics endpoints |
| `frontend/src/pages/Analytics.tsx` | CREATE | Historical performance dashboard |
| `backend/ml/tests/test_backtest.py` | CREATE | Backtest tests |
| `backend/api/tests/test_analytics.py` | CREATE | Analytics API tests |

### Database Changes
- `backtest_results` table (model_id, game_id, predicted_probability, actual_outcome, edge, roi, created_at)
- `model_evaluations` table (model_id, evaluated_at, accuracy, calibration_error, avg_roi, brier_score)
- Add `actual_outcome` column to `games` table (updated after game ends)

### Backend Tasks
1. Implement `BacktestService.run_backtest(model_id, date_range)` — replay predictions against actuals
2. Implement `BacktestService.evaluate_model(model_id)` — produce metrics
3. Create `/api/analytics/performance?model_id=X` endpoint
4. Create `/api/analytics/portfolio-history` endpoint
5. Set up scheduled backtests (daily)

### Frontend Tasks
1. Build `Analytics` page with performance charts
2. Display model accuracy/calibration/ROI over time
3. Show backtest results in table format

### Tests
- Backtest matches predictions to actual outcomes
- Accuracy calculation is correct
- Brier score calculation is correct
- Calibration error matches System Plays engine output
- ROI calculation includes bet sizing from Kelly

### Verification Checklist
- [ ] Backtest runs against historical data
- [ ] Model evaluation produces correct metrics
- [ ] Analytics dashboard shows trends
- [ ] Auto-backtest triggers when game result arrives

### Definition of Done
Backtesting engine runs. Historical predictions are matched against actual results. Model performance metrics are calculated and displayed.

### Out of Scope
- Model retraining (Sprint 13)
- Live model deployment (Sprint 13)

### Next Sprint Dependencies
- Sprint 13 needs backtest results for model evaluation

---

## Sprint 13 — ML Pipeline & Explainability

### Purpose
Set up the ML pipeline infrastructure. Define the model interface, feature schema, training pipeline, and explainability output. No actual model training, but the framework is ready.

### Goal
The backend has a `ProbabilityModel` interface that can be swapped between user-input, stub, and a trained model. Feature engineering pipeline is defined. Explainability engine returns top factors per prediction.

### Why Now
The backtesting engine (Sprint 12) is ready. We need the ML infrastructure to feed predictions into the pipeline. GPT listed this as the foundation for the "Model → Simulation → EV → Recommendation" chain. This sprint makes the transition from "user inputs probability" to "ML model inputs probability" a drop-in replacement.

### Background
The ML pipeline follows the recommendation lifecycle: Game Imported → Features Generated → Prediction → Simulation → EV → System Play. We set up the interface but don't train actual models yet. The UserInputModel is the default — the user replaces it.

### Deliverables
- `ProbabilityModel` ABC with `predict()` and `get_confidence()`
- `UserInputModel` — wraps user-input probability
- `StubModel` — returns fixed probability (for testing)
- Feature schema (30+ features)
- `extract_features()` function
- Training pipeline structure (placeholder)
- Model registry interface
- Explainability: top factors per prediction
- `/api/models/predict` endpoint

### Acceptance Criteria
- [ ] Code committed and `ruff check` passes
- [ ] `pytest` covers model interface + feature extraction
- [ ] UserInputModel returns correct probability
- [ ] Feature extraction produces correct shape (30+ features)
- [ ] Explainability returns top 5 factors

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/ml/models/base.py` | CREATE | ProbabilityModel ABC |
| `backend/ml/models/user_input.py` | CREATE | UserInputModel |
| `backend/ml/models/stub.py` | CREATE | StubModel |
| `backend/ml/features/schema.py` | CREATE | Feature definitions |
| `backend/ml/features/engineering.py` | CREATE | extract_features() |
| `backend/ml/explainability.py` | CREATE | Top factors + explanation |
| `backend/ml/pipeline.py` | CREATE | TrainingPipeline structure |
| `backend/api/models.py` | CREATE | /api/models/* endpoints |
| `backend/schemas/features.py` | CREATE | Feature Pydantic schemas |
| `backend/schemas/model.py` | CREATE | ModelInfo, Prediction schemas |

### Database Changes
- `ml_models` table: id, name, version, trained_at, training_dataset, features_used, accuracy, calibration_score, roi, cross_validation, notes, is_production, is_archived, model_path
- `model_predictions` table: id, model_id, game_id, predicted_probability, confidence, created_at

### Backend Tasks
1. Create `ProbabilityModel` ABC with `predict()` + `get_confidence()`
2. Create `UserInputModel` — wraps user input probability
3. Create `StubModel` — for testing
4. Define feature schema (odds, team stats, injuries, line movement, etc.)
5. Create `extract_features()` — raw data → feature vector
6. Create `explainability.py` — top factors with weights
7. Create `TrainingPipeline` class (stub — raises NotImplementedError)
8. Create `/api/models/predict` and `/api/models/list` endpoints

### Frontend Tasks
1. Add "Model" selector to System Plays (User Input / Stub / Trained)
2. Display model confidence when available
3. Add ExplainabilityPanel to recommendation views
4. Show top factors with + / - indicators

### Tests
- UserInputModel.predict() returns user's probability
- StubModel.predict() returns probability in [0, 1]
- Feature extraction produces correct shape (30+ features)
- Explainability returns top 5 factors with weights
- `/api/models/predict` returns probability + confidence + factors

### Verification Checklist
- [ ] Model interface is swappable
- [ ] Feature schema covers all data sources
- [ ] Feature extraction works
- [ ] Explainability output matches spec
- [ ] API endpoints respond correctly

### Definition of Done
ML pipeline infrastructure is in place. Model interface is swappable. Feature schema is defined. Explainability engine returns top factors. Training pipeline structure exists.

### Out of Scope
- Actual model training (future sprint)
- Model performance evaluation (uses Sprint 12's backtesting)

### Next Sprint Dependencies
- Sprint 14 uses model predictions for Intelligence Score

---

## Sprint 14 — Intelligence Score, Portfolio & Testing

### Purpose
Implement the Intelligence Score (SIP's unique differentiator), Portfolio Construction algorithm, and a comprehensive test suite + packaging.

### Goal
Every recommendation gets an Intelligence Score (0–100) aggregating probability, simulation, EV, confidence, and calibration. The Portfolio Construction algorithm creates daily bet portfolios with confidence-band allocation. Plus full test coverage and Electron packaging.

### Why Now
All the building blocks are in place: simulation engine, System Plays calibration, backtesting, ML pipeline, explainability. Now we deliver the "smarts" — the scoring algorithm that makes SIP different from a calculator, and the portfolio construction that applies portfolio theory to betting. Testing + packaging ensures we can ship.

### Background
The Intelligence Score weights: Probability 25%, Simulation 25%, EV 25%, Model Confidence 15%, Calibration 10%. Bonuses for positive EV, good calibration, and simulation agreement. The Portfolio algorithm ranks all recommendations by score, allocates by confidence band (High: 40%, Medium: 30%, Low: 20%), and caps total exposure at 80%.

### Deliverables
- Intelligence Score calculation function
- Portfolio Construction algorithm
- `/api/portfolio` endpoint
- Portfolio page UI
- IntelligenceScore component
- Comprehensive test suite (backend + frontend)
- Electron packaging configuration
- Test coverage report (>85%)

### Acceptance Criteria
- [ ] Code committed and lint passes
- [ ] Backend test coverage > 85%
- [ ] Frontend test coverage > 80%
- [ ] Intelligence Score calculation matches formula
- [ ] Portfolio correctly allocates by confidence bands
- [ ] Electron app builds successfully
- [ ] All existing tests still pass

### Files / Folders

| Path | Action | Description |
|------|--------|-------------|
| `backend/ml/recommend.py` | CREATE | RecommendationService + Intelligence Score |
| `backend/ml/portfolio.py` | CREATE | Portfolio construction algorithm |
| `backend/api/portfolio.py` | CREATE | /api/portfolio endpoint |
| `backend/schemas/portfolio.py` | CREATE | Portfolio Pydantic schemas |
| `backend/ml/tests/test_recommend.py` | CREATE | Intelligence Score tests |
| `backend/ml/tests/test_portfolio.py` | CREATE | Portfolio tests |
| `frontend/src/pages/Portfolio.tsx` | CREATE | Portfolio page |
| `frontend/src/components/IntelligenceScore.tsx` | CREATE | Score breakdown component |
| `frontend/src/components/PortfolioView.tsx` | CREATE | Portfolio layout |
| `frontend/src/services/portfolioApi.ts` | CREATE | Portfolio API client |
| `frontend/src/__tests__/IntelligenceScore.test.tsx` | CREATE | Component tests |
| `frontend/src/__tests__/PortfolioView.test.tsx` | CREATE | Component tests |
| `backend/tests/test_e2e.py` | CREATE | End-to-end: simulate → score → portfolio |

### Database Changes
- `portfolios` table: id, date, total_risk, expected_roi, kelly_exposure, model_id
- `portfolio_items` table: id, portfolio_id, game_id, model_id, confidence_level, bet_type, stake, predicted_probability, ev, recommendation_stars

### Backend Tasks
1. Implement Intelligence Score calculation from RecommendationService
2. Implement Portfolio Construction algorithm (confidence bands, Kelly exposure)
3. Create `/api/portfolio` endpoint
4. Create comprehensive test suite with coverage > 85%
5. Run full test suite to verify no regressions

### Frontend Tasks
1. Build `IntelligenceScore` component — score breakdown + stars + risk level
2. Build `PortfolioView` — portfolio layout with confidence bands
3. Build `Portfolio` page — fetch + display portfolio
4. Add `ExplainabilityPanel` to recommendation views
5. Create comprehensive frontend test suite (>80% coverage)
6. Configure coverage reporting

### Tests
- Intelligence Score matches formula exactly
- Portfolio correctly allocates by confidence bands
- `/api/portfolio` returns all required fields
- Integration: simulate → score → portfolio produces correct pipeline
- Test coverage report shows >85% backend, >80% frontend
- No regressions in existing tests

### Verification Checklist
- [ ] Intelligence Score displays correctly with breakdown
- [ ] Portfolio shows confidence bands + key metrics
- [ ] "Add to Portfolio" button works from recommendations
- [ ] Backend test coverage > 85%
- [ ] Frontend test coverage > 80%
- [ ] Electron app builds with `npm run build`

### Definition of Done
Intelligence Score and Portfolio Construction work end-to-end. Test coverage is >85% backend, >80% frontend. Electron app builds successfully. All existing tests pass.

### Out of Scope
- Actual ML model training (future)
- Live deployment / production hosting
- Mobile companion app

### Next Sprint Dependencies
- None — this is the final sprint of the current roadmap

---

## Sprint Planning Cadence

Each sprint follows this review structure:

1. **Sprint Planning** — Review goals, assign tasks, estimate
2. **Daily Standup** — What was done yesterday, what's today's focus, blockers
3. **Sprint Review** — Demo completed work to stakeholders
4. **Sprint Retrospective** — What went well, what can improve, action items

### Sprint Length
- **10 working days** per sprint (2 weeks)
- **Demo Friday** of each sprint — show working features
- **Retro Monday** — 30 min retro, planning for next sprint

### Definition of Done (Global)
A feature is "done" when:
1. Code is written and reviewed
2. Unit tests cover >80% of new logic
3. Integration tests pass
4. Documentation is updated
5. Feature is demonstrable in the running app
6. No critical bugs found in QA

---

## Milestone Tracker

| Milestone | Target Sprint | Description |
|-----------|---------------|-------------|
| Alpha | Sprint 6 | Basic simulation runs in UI |
| MVP Release | Sprint 8 | Full simulation workspace with charts + strategy saving |
| Beta | Sprint 11 | System Plays + Parlay + Bankroll Strategies |
| Data-Driven | Sprint 9 | Live odds integration |
| ML Ready | Sprint 13 | ML pipeline infrastructure complete |
| Full Product | Sprint 14 | Intelligence Score, Portfolio, all tests passing |

> **Note on future expansion:** If needed, Sprint 13 can be split into "ML Training Pipeline" and "Prediction Service" for finer granularity. Sprint 14 can be split into "Intelligence Score & Portfolio" and "Testing & Packaging." This keeps each sprint at a coherent, testable milestone size.

---

*This document is the single source of truth for what gets built and when. Sprint boundaries are firm — scope creep pushes to the next sprint, not extends the current one.*