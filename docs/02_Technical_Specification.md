# 02_Technical_Specification.md

# Betsim — Technical Specification

**Project:** Betsim - Monte Carlo Betting Simulator  
**Version:** 1.0  
**Last Updated:** 2026-08-01

---

## Table of Contents

1. [Vision & Goals](#1-vision--goals)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Core Data Flow](#3-core-data-flow)
4. [Technology Stack](#4-technology-stack)
5. [Folder Structure](#5-folder-structure)
6. [Simulation Engine](#6-simulation-engine)
7. [API Specification](#7-api-specification)
8. [Database Design](#8-database-design)
9. [System Plays Engine](#9-system-plays-engine)
10. [Data Collection Pipeline](#10-data-collection-pipeline)
11. [ML Pipeline](#11-ml-pipeline)
12. [Service Responsibilities](#12-service-responsibilities)
13. [Recommendation Lifecycle](#13-recommendation-lifecycle)
14. [Model Registry](#14-model-registry)
15. [Explainability](#15-explainability)
16. [Intelligence Score](#16-intelligence-score)
17. [Portfolio Construction](#17-portfolio-construction)
18. [AI Agent Guide](#18-ai-agent-guide)
19. [Design Decisions](#19-design-decisions)

---

## 1. Vision & Goals

### Vision

A desktop application that uses Monte Carlo simulation to help bettors understand risk, variance, and edge — not to predict winners, but to make the math of betting transparent and educational.

### Goals

| Goal | Description |
|------|-------------|
| **Educational** | Show bettors how variance, bankroll management, and edge interact |
| **Transparent** | No fake "prediction confidence" — show the math, warts and all |
| **Practical** | User can simulate 1,000–100,000 runs in seconds |
| **Local-First** | Runs entirely on the user's machine — no cloud dependency |
| **Extensible** | Clean architecture to plug in ML models and live data later |

### Non-Goals

- Providing betting picks or "sure thing" predictions
- Real-money betting or integration with sportsbooks
- Live in-play odds updates (deferred)
- Mobile app (deferred — see Product Design)

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Electron App                          │
│                                                          │
│  ┌──────────────────────┐  ┌────────────────────────┐  │
│  │   React Frontend      │  │   FastAPI Backend      │  │
│  │   (Vite + TS)         │  │   (Python)             │  │
│  │                        │  │                        │  │
│  │  - Simulation Forms    │  │  - Simulation Engine   │  │
│  │  - Result Charts       │  │  - System Plays Engine │  │
│  │  - Strategy Mgmt       │  │  - Odds API Client     │  │
│  │  - Parlay Builder      │  │  - ML Pipeline (stub)  │  │
│  │                        │  │                        │  │
│  │  HTTP (localhost)      │  │  HTTP (localhost:8000)│  │
│  └──────────┬─────────────┘  └─────────┬──────────────┘  │
│             │                          │                 │
│  Renderer    │                          │  Python Server  │
│  Process      │                          │  (Uvicorn)     │
└──────────────┼──────────────────────────┼────────────────┘
               │                          │
         IPC   │                          │
    (main ↔ renderer)                     │
               │                          │
┌──────────────┴────────────┐            │
│        Electron Main       │            │
│        Process             │            │
└───────────────────────────┘            │
               │                          │
               └────── SQLite ────────────┘
                     ~/.betsim/
```

### Architecture Layers

| Layer | Technology | Responsibility |
|-------|-----------|----------------|
| **Desktop Shell** | Electron | App lifecycle, OS integration, packaging |
| **UI Layer** | React + TypeScript | User interactions, forms, charts |
| **API Layer** | FastAPI | REST endpoints, request/response validation |
| **Engine Layer** | Python (NumPy) | Monte Carlo simulation, metrics calculation |
| **Persistence** | SQLite | Strategy storage, simulation results, cached odds |
| **External** | TheOddsAPI | Live sports odds (integrated in Sprint 9) |

### Communication Flow

1. **Electron → React Renderer:** IPC for app lifecycle events (auto-updates, dialogs)
2. **React Renderer → FastAPI:** HTTP requests to `http://localhost:8000/api/*`
3. **FastAPI → SQLite:** SQLAlchemy ORM for persistence
4. **FastAPI → TheOddsAPI:** HTTP requests for live odds (background scheduler)
5. **FastAPI → ML Model:** Direct Python import (model runs in-process)

---

## 3. Core Data Flow

### Simulation Data Flow

```
User Input
    │
    ▼
[SimulationForm] → validates → [SimulationRequest]
    │
    ▼
API: POST /api/simulate
    │
    ▼
[simulate_batch(params)] in engine.py
    │  ┌─────────────────────────────────────┐
    │  │ for run in range(1000):             │
    │  │   bankroll = start                  │
    │  │   for bet in range(num_bets):       │
    │  │     stake = calc_stake(strategy)    │
    │  │     win = random() < win_prob       │
    │  │     bankroll += win ? profit : -stake│
    │  │   trajectories.append(trajectory)   │
    │  └─────────────────────────────────────┘
    │
    ▼
[metrics = calculate_metrics(trajectories)]
    │
    ▼
[SimulationResponse] ← JSON
    │
    ▼
[SimulationResults] ← renders charts + tables
```

### System Plays Data Flow

```
User Estimate (e.g., 60% win prob)
    │
    ▼
API: POST /api/system-plays
    │
    ▼
[calibrate_model(params)]
    │  ┌─────────────────────────────────────┐
    │  │ Model says: 60%                     │
    │  │ Sim reality: 60% (same prob)        │
    │  │ Actual win rate: ~60% (±variance)   │
    │  │ Calibration error: ~0%              │
    │  └─────────────────────────────────────┘
    │
    ▼
[CalibrationReport] ← JSON
    │
    ▼
[CalibrationChart] ← shows stated vs. actual
```

> The System Plays Engine validates whether a probability model is calibrated. In MVP, the "model" is the user's input. In the future, it's an ML model.

---

## 4. Technology Stack

### Backend

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | ML ecosystem, NumPy for simulation speed |
| Framework | FastAPI | Auto-generated OpenAPI docs, async support, type validation |
| ASGI Server | Uvicorn | Lightweight, production-ready |
| ORM | SQLAlchemy 2.0 | Mature, flexible, good SQLite support |
| Schema Validation | Pydantic v2 | Built into FastAPI |
| Simulation | NumPy | Vectorized RNG for fast Monte Carlo |
| Testing | Pytest | Simple, fixtures, async support |
| Linting | Ruff | Fast, all-in-one (flake + isort + black) |

### Frontend

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | React 18+ | Component-based, large ecosystem |
| Language | TypeScript | Type safety, IDE support |
| Build | Vite | Fast dev server, HMR |
| Desktop | Electron 28+ | Cross-platform desktop apps |
| Charts | Recharts | Built on D3, React-friendly, lightweight |
| HTTP Client | Axios | Interceptors, request/response typing |
| State Management | React hooks + Context | Sufficient for MVP scope |
| Testing | Vitest + React Testing Library | Jest-compatible, fast |
| Styling | Tailwind CSS | Utility-first, no CSS file management |
| Formatting | Prettier + ESLint | Consistent code style |

### DevOps

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Package Manager | npm (root workspace) | Manages both frontend + electron |
| Python Env | venv + requirements.txt | Simple, no Poetry needed for MVP |
| CI | GitHub Actions | Free for public repos, integrates with GitHub |
| Packaging | electron-builder | Produces .exe/.dmg/.AppImage |

### Development Constraints

| Constraint | Detail |
|-----------|--------|
| Python Version | 3.11+ required (match backend dev env) |
| Node Version | 20+ required |
| Database Location | `~/.betsim/betsim.db` (user home directory) |
| Backend Port | 8000 (localhost only, no external exposure) |

---

## 5. Folder Structure

```
betsim/
├── README.md
├── package.json                    # Root workspace scripts
├── electron-builder.json           # Electron packaging config
├── .gitignore
├── backend/                        # FastAPI application
│   ├── main.py                     # App entry point, router registration
│   ├── config.py                   # Pydantic settings (API keys, paths)
│   ├── database.py                 # SQLAlchemy engine + session
│   ├── requirements.txt            # Python dependencies
│   ├── ruff.toml                   # Linter config
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── strategy.py             # Strategy model
│   │   ├── simulation.py           # SimulationRun, SimulationResult
│   │   ├── odds.py                 # GameOdds, Team (Sprint 9)
│   │   ├── injury.py               # Injury data (Sprint 9)
│   │   ├── ml_model.py             # Model metadata (Sprint 13)
│   │   ├── portfolio.py            # Portfolio + items (Sprint 14)
│   │   ├── backtest.py             # Backtest results (Sprint 12)
│   │   └── system_play.py          # System play results (Sprint 10)
│   ├── schemas/                    # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── strategy.py             # StrategyCreate, StrategyRead
│   │   ├── simulation.py           # SimulationRequest, SimulationResponse
│   │   ├── system_plays.py         # CalibrationReport schema
│   │   ├── parlay.py               # ParlayRequest, ParlayResponse
│   │   ├── odds.py                 # GameOdds schemas (Sprint 9)
│   │   ├── features.py             # FeatureVector schema (Sprint 13)
│   │   ├── portfolio.py            # Portfolio schemas (Sprint 14)
│   │   ├── model.py                # ModelInfo, Prediction schemas (Sprint 13)
│   │   └── __init__.py
│   ├── crud/                       # CRUD operations (StorageService)
│   │   ├── __init__.py
│   │   ├── strategy.py
│   │   ├── simulation.py
│   │   ├── odds.py
│   │   ├── models.py
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── test_strategy.py
│   │       └── test_simulation.py
│   ├── api/                        # API routers
│   │   ├── __init__.py
│   │   ├── deps.py                 # DB session dependency
│   │   ├── simulation.py           # /api/simulate
│   │   ├── strategies.py           # /api/strategies
│   │   ├── system_plays.py         # /api/system-plays
│   │   ├── parlay.py               # /api/parlay/simulate
│   │   ├── odds.py                 # /api/odds/* (Sprint 9)
│   │   └── models.py               # /api/models/* (Sprint 13)
│   ├── simulation/                 # SimulationService — pure logic, no DB/API
│   │   ├── __init__.py
│   │   ├── monte_carlo.py          # simulate_once, simulate_batch
│   │   ├── odds.py                 # OddsConversion (American ↔ Decimal ↔ Prob)
│   │   ├── risk.py                 # risk_of_ruin, max_drawdown
│   │   ├── distribution.py         # percentile calc, histogram bins
│   │   ├── bankroll.py             # BankrollService: flat, %, Kelly, half-Kelly
│   │   ├── parlay.py               # Parlay probability + simulation
│   │   ├── calibration.py          # System Plays calibration (Sprint 10)
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── test_monte_carlo.py
│   │       ├── test_odds.py
│   │       ├── test_risk.py
│   │       ├── test_distribution.py
│   │       ├── test_bankroll.py
│   │       ├── test_parlay.py
│   │       └── test_calibration.py
│   ├── ml/                         # ML pipeline
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # ProbabilityModel ABC (Sprint 13)
│   │   │   ├── user_input.py       # UserInputModel (Sprint 13)
│   │   │   └── stub.py             # StubModel (Sprint 13)
│   │   ├── features/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py           # Feature definitions (Sprint 13)
│   │   │   └── engineering.py      # extract_features (Sprint 13)
│   │   ├── backtest.py             # BacktestService (Sprint 12)
│   │   ├── recommend.py            # RecommendationService (Sprint 10)
│   │   ├── pipeline.py             # TrainingPipeline structure (Sprint 13)
│   │   └── tests/
│   │       ├── conftest.py
│   │       ├── test_models.py
│   │       ├── test_features.py
│   │       └── test_backtest.py
│   ├── services/                   # External integrations
│   │   ├── __init__.py
│   │   ├── odds_api.py             # TheOddsAPI client (Sprint 9)
│   │   ├── scheduler.py            # SchedulerService (Sprint 9)
│   │   ├── cache.py                # In-memory cache (Sprint 9)
│   │   └── tests/
│   │       ├── conftest.py
│   │       └── test_odds_api.py
│   └── tests/                      # Top-level integration tests
│       ├── conftest.py
│       ├── test_api.py
│       └── test_e2e.py
├── frontend/                       # React + Electron app
│   ├── package.json
│   ├── electron-main.js            # Electron main process
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── eslint.config.js
│   └── src/
│       ├── main.tsx                # React entry
│       ├── App.tsx                 # Root component + routing
│       ├── types/                  # TypeScript types
│       │   ├── simulation.ts
│       │   └── strategy.ts
│       ├── services/
│       │   ├── api.ts              # Axios client
│       │   └── strategiesApi.ts
│       ├── hooks/
│       │   ├── useSimulation.ts    # React hook for sim state
│       │   └── useStrategies.ts    # React hook for strategy CRUD
│       ├── pages/
│       │   ├── SimulationWorkspace.tsx
│       │   ├── SystemPlays.tsx
│       │   ├── ParlaySimulator.tsx
│       │   ├── Strategies.tsx
│       │   └── Analytics.tsx       # Future: historical trends
│       ├── components/
│       │   ├── SimulationForm.tsx
│       │   ├── ResultsDisplay.tsx
│       │   ├── BankrollChart.tsx
│       │   ├── DistributionChart.tsx
│       │   ├── MetricsTable.tsx
│       │   ├── StrategyCard.tsx
│       │   ├── ParlayBuilder.tsx
│       │   └── BankrollStrategySelector.tsx
│       └── __tests__/
│           ├── conftest.tsx
│           ├── SimulationForm.test.tsx
│           ├── BankrollChart.test.tsx
│           └── ResultsDisplay.test.tsx
└── docs/
    ├── 01_Sprint_Plan.md
    ├── 02_Technical_Specification.md  ← this file
    └── 03_Product_Design.md
```

---

## 6. Simulation Engine

### Core Data Model

```typescript
interface SimulationRequest {
  odds_american: number;      // e.g., -110, +150
  win_probability: number;    // 0.0–1.0 (e.g., 0.55 for 55%)
  bankroll: number;           // starting bankroll in $ (e.g., 1000)
  bet_size: number;           // dollar amount or percentage depending on type
  bet_size_type: 'flat' | 'percentage' | 'kelly' | 'half_kelly';
  num_bets: number;           // bets per simulation run (1–10,000)
  num_simulations: number;    // simulation runs (1,000–100,000)
  seed?: number;              // optional, for reproducible results
}
```

### Odds Conversion

| Format | Formula | Example |
|--------|---------|---------|
| American → Decimal | `if > 0: (odds + 100) / 100 else: (odds + 100) / -100` → then `|result|` | -110 → 1.909, +150 → 2.500 |
| American → Implied Prob | `if > 0: 100 / (odds + 100) else: -odds / (-odds + 100)` | -110 → 52.38%, +150 → 40.00% |
| Implied Prob → Decimal | `1 / implied_prob` | 52.38% → 1.909 |
| Fair Odds (no vig) | Remove bookmaker margin: `fair_prob = implied_prob / sum(all_implied_probs)` | -110/-110 → fair prob = 50% each |

#### Python Implementation

```python
class OddsConversion:
    @staticmethod
    def american_to_decimal(odds_american: int) -> float:
        if odds_american > 0:
            return (odds_american + 100) / 100
        else:
            return (odds_american + 100) / abs(odds_american)

    @staticmethod
    def american_to_implied_prob(odds_american: int) -> float:
        if odds_american > 0:
            return 100 / (odds_american + 100)
        else:
            return abs(odds_american) / (abs(odds_american) + 100)

    @staticmethod
    def kelly_criterion(odds_decimal: float, win_prob: float) -> float:
        """Returns fraction of bankroll to bet. b = decimal - 1"""
        b = odds_decimal - 1
        p = win_prob
        q = 1 - win_prob
        return (b * p - q) / b  # = p - q/b
```

### Monte Carlo Simulation

```python
def simulate_once(
    odds_decimal: float,
    win_prob: float,
    bankroll: float,
    bet_size: float,
    bet_size_type: str,
    num_bets: int,
    rng: np.random.Generator,
) -> list[float]:
    """Run a single simulation series. Returns bankroll trajectory."""
    trajectory = [bankroll]
    profit_per_win = bet_size_stake * (odds_decimal - 1)  # net profit
    
    for _ in range(num_bets):
        if bankroll <= 0:
            trajectory.append(0)
            continue
        
        # Calculate stake based on strategy
        if bet_size_type == 'flat':
            stake = bet_size  # fixed dollar amount
        elif bet_size_type == 'percentage':
            stake = bankroll * bet_size  # bet_size is fraction (e.g., 0.05)
        elif bet_size_type in ('kelly', 'half_kelly'):
            kelly_frac = kelly_criterion(odds_decimal, win_prob)
            stake = bankroll * (kelly_frac if bet_size_type == 'kelly' else kelly_frac / 2)
        
        # Don't bet more than you have
        stake = min(stake, bankroll)
        
        # Simulate the bet
        if rng.random() < win_prob:
            bankroll += stake * (odds_decimal - 1)  # profit
        else:
            bankroll -= stake
        
        trajectory.append(bankroll)
    
    return trajectory
```

### Batch Simulation

```python
def simulate_batch(
    odds_decimal: float,
    win_prob: float,
    bankroll: float,
    bet_size: float,
    bet_size_type: str,
    num_bets: int,
    num_simulations: int = 1000,
    seed: Optional[int] = None,
) -> SimulationBatchResult:
    """Run num_simulations independent simulations."""
    rng = np.random.default_rng(seed)
    trajectories = []
    final_bankrolls = []
    max_drawdowns = []
    
    for _ in range(num_simulations):
        traj = simulate_once(odds_decimal, win_prob, bankroll,
                            bet_size, bet_size_type, num_bets, rng)
        trajectories.append(traj)
        final_bankrolls.append(traj[-1])
        max_drawdowns.append(calculate_max_drawdown(traj))
    
    return SimulationBatchResult(
        final_bankrolls=final_bankrolls,
        trajectories=trajectories,
        max_drawdowns=max_drawdowns,
        metrics=calculate_metrics(final_bankrolls, trajectories, max_drawdowns),
    )
```

### Metrics Calculation

```python
def calculate_metrics(
    final_bankrolls: list[float],
    trajectories: list[list[float]],
    max_drawdowns: list[float],
) -> Metrics:
    final = np.array(final_bankrolls)
    starting = trajectories[0][0]
    
    return Metrics(
        win_pct=float(np.mean(final > starting)),
        avg_ending_bankroll=float(np.mean(final)),
        median_ending_bankroll=float(np.median(final)),
        std_dev=float(np.std(final)),
        min_bankroll=float(np.min(final)),
        max_bankroll=float(np.max(final)),
        risk_of_ruin=float(np.mean(final <= 0)),
        avg_max_drawdown=float(np.mean(max_drawdowns)),
        worst_case_drawdown=float(np.min(max_drawdowns)),
        ev_per_bet=ev_per_bet,  # win_prob * profit_per_win - (1-win_prob) * stake
        ev_total=ev_per_bet * num_bets,
        # Trajectory summaries for charts
        trajectory_percentiles={
            'median': np.percentile(trajectories, 50, axis=0),
            'p10': np.percentile(trajectories, 10, axis=0),
            'p90': np.percentile(trajectories, 90, axis=0),
            'min': np.min(trajectories, axis=0),
            'max': np.max(trajectories, axis=0),
        }
    )
```

### Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| 1,000 simulations × 100 bets | < 500ms | NumPy vectorized RNG |
| 10,000 simulations × 100 bets | < 2s | Acceptable wait time |
| 100,000 simulations × 100 bets | < 15s | Upper bound, shows warning |
| Memory per 1,000 × 1,000 | < 10MB | Trajectory arrays stored |

> Default: 5,000 simulations × 100 bets. Users can adjust up to 100,000.

---

## 7. API Specification

All endpoints are under `http://localhost:8000/api/`.

### POST `/api/simulate`

Run a Monte Carlo simulation.

**Request:**
```json
{
  "odds_american": -110,
  "win_probability": 0.55,
  "bankroll": 1000,
  "bet_size": 50,
  "bet_size_type": "flat",
  "num_bets": 100,
  "num_simulations": 5000,
  "seed": 42
}
```

**Response (201):**
```json
{
  "simulation_id": "uuid",
  "metrics": {
    "win_pct": 0.62,
    "avg_ending_bankroll": 1240.50,
    "median_ending_bankroll": 1180.00,
    "std_dev": 350.25,
    "risk_of_ruin": 0.18,
    "ev_per_bet": 2.27,
    "ev_total": 227.00,
    "worst_case_drawdown": -450.00,
    "avg_max_drawdown": -320.00
  },
  "distribution": {
    "bins": [800, 900, 1000, 1100, 1200, 1300, 1400],
    "counts": [50, 100, 500, 1200, 1800, 1200, 150]
  },
  "trajectory": {
    "median": [1000, 1002, 1005, ...],
    "p10": [1000, 995, 990, ...],
    "p90": [1000, 1008, 1012, ...],
    "min": [1000, 990, 985, ...],
    "max": [1000, 1015, 1020, ...]
  }
}
```

### Strategy CRUD

#### GET `/api/strategies`
List all saved strategies.

**Response (200):**
```json
[{"id": 1, "name": "My NFL Strategy", "odds_american": -110, "win_probability": 0.55, ...}]
```

#### POST `/api/strategies`
Save a new strategy.

**Request:**
```json
{"name": "NFL Week 1", "odds_american": -110, "win_probability": 0.55, "bankroll": 1000, "bet_size": 50, "bet_size_type": "flat", "num_bets": 100, "num_simulations": 5000}
```

#### GET `/api/strategies/{id}`
#### PUT `/api/strategies/{id}`
#### DELETE `/api/strategies/{id}`

### POST `/api/simulate/{strategy_id}`
Run a simulation using a saved strategy. Accepts overrides (e.g., different `num_simulations`).

### POST `/api/system-plays`

Run model calibration. See System Plays Engine section below.

### POST `/api/parlay/simulate`

Simulate a parlay. Accepts a list of selections.

### GET `/api/odds/games?sport=nba` (Sprint 9)

List live games with odds from TheOddsAPI.

### POST `/api/models/predict` (Sprint 13)

Get probability prediction from ML model.

### API Contract Summary

| Endpoint | Method | Input | Output | Used By |
|----------|--------|-------|--------|---------|
| `/api/simulate` | POST | SimulationRequest (odds, prob, bankroll, bet params) | SimulationResponse (metrics, distribution, trajectory) | SimulationWorkspace, SystemPlays |
| `/api/strategies` | GET | — | List[StrategyRead] | StrategiesPage |
| `/api/strategies` | POST | StrategyCreate | StrategyRead | SimulationWorkspace ("Save") |
| `/api/strategies/{id}` | GET | id (path) | StrategyRead | StrategyEditor |
| `/api/strategies/{id}` | PUT | id (path), StrategyUpdate | StrategyRead | StrategyEditor |
| `/api/strategies/{id}` | DELETE | id (path) | 204 No Content | StrategiesPage |
| `/api/simulate/{strategy_id}` | POST | id (path), overrides (optional JSON body) | SimulationResponse | StrategiesPage (Run button) |
| `/api/system-plays` | POST | SystemPlayRequest (same as SimulationRequest) | CalibrationReport | SystemPlaysPage |
| `/api/parlay/simulate` | POST | ParlayRequest (list of selections) | ParlayResponse (metrics, variance) | ParlaySimulator |
| `/api/odds/games` | GET | sport (query param) | List[GameOddsDTO] | SimulationWorkspace (live odds selector) |
| `/api/models/list` | GET | — | List[ModelInfo] | Settings, SystemPlays (model selector) |
| `/api/models/predict` | POST | game_id or FeatureVector | ModelPrediction (probability, confidence, factors) | PredictionService |
| `/api/parlay/simulate` | POST | ParlayRequest (selections, bankroll, params) | ParlayResponse (combined prob, payout, metrics) | ParlaySimulator |

### Error Responses

| HTTP Status | Meaning | Response Body |
|-------------|---------|---------------|
| 422 | Validation Error | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| 404 | Resource Not Found | `{"detail": "Strategy not found"}` |
| 500 | Internal Error | `{"detail": "Internal server error"}` |

---

## 8. Database Design

### ER Diagram

```
┌──────────┐     ┌──────────┐     ┌────────────────┐
│  teams   │     │  games   │     │   game_odds    │
└────┬─────┘     └─────┬────┘     └──────┬─────────┘
     │                 │                  │
     │  home_team_id   │  id              │  game_id
     │  away_team_id   │                  │
     ▼                 ▼                  ▼
┌──────────┐     ┌──────────┐     ┌────────────────┐
│ injuries │     │ game_odds│     │  raw_odds      │
└──────────┘     └──────────┘     └────────────────┘


┌──────────┐     ┌──────────────┐     ┌────────────────┐
│ strategies│────│ simulation_  │────│ simulation_    │
└──────────┘     │ runs         │     │ results        │
                 └──────────────┘     └────────────────┘


┌────────────┐     ┌────────────────┐
│ ml_models  │────│ model_         │
└────────────┘     │ predictions    │
                   └────────────────┘


┌────────────┐     ┌────────────────┐
│ portfolios │────│ portfolio_     │
└────────────┘     │ items          │
                   └────────────────┘

                    ┌──────────────┐
                    │ system_play_ │
                    │ results      │
                    └──────────────┘

                    ┌──────────────┐
                    │ backtest_    │
                    │ results      │
                    └──────────────┘

                    ┌──────────────┐
                    │ model_       │
                    │ evaluations  │
                    └──────────────┘
```

### Tables

#### `teams`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Master list of sports teams across all leagues. Enables roster/injury tracking and team-level stats. |
| **Columns** | id (INTEGER PK), name (STRING(100)), sport (STRING(20)), league (STRING(50)), city (STRING(50)), abbreviation (STRING(10)), created_at (DATETIME) |
| **Relationships** | games (home_team_id, away_team_id), injuries (team_id), raw_injuries (team_id) |
| **Indexes** | sport, league, name |

#### `games`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Stores every historical and future game across all sports. Central entity for all other tables. |
| **Columns** | id (STRING PK — external provider ID), sport (STRING(20)), league (STRING(50)), home_team_id (FK→teams), away_team_id (FK→teams), home_score (INTEGER), away_score (INTEGER), game_time (DATETIME), status (STRING(20) — scheduled/live/final/postponed), season (STRING(10)), week (INTEGER), venue (STRING(100)), created_at (DATETIME) |
| **Relationships** | teams (home_team_id, away_team_id), game_odds, model_predictions, backtest_results, system_play_results |
| **Indexes** | sport, game_time, status, season, home_team_id, away_team_id |

#### `game_odds`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Normalized betting odds from all sportsbooks for every game. Stored with timestamp to track line movement. |
| **Columns** | id (INTEGER PK), game_id (FK→games), sportsbook (STRING(50)), market_type (STRING(20) — moneyline/spread/total), outcome_name (STRING(50)), odds_american (INTEGER), odds_decimal (FLOAT), implied_probability (FLOAT), is_no_vig (BOOLEAN), timestamp (DATETIME), created_at (DATETIME) |
| **Relationships** | games (game_id) |
| **Indexes** | game_id, sportsbook, market_type, timestamp |

#### `raw_odds`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Raw, unmodified odds data from each provider before normalization. Used for debugging and provider comparison. |
| **Columns** | id (INTEGER PK), provider (STRING(50)), provider_game_id (STRING(100)), sport (STRING(20)), home_team (STRING(100)), away_team (STRING(100)), market_type (STRING(20)), outcome_name (STRING(50)), odds_american (INTEGER), odds_decimal (FLOAT), timestamp (DATETIME), raw_json (TEXT), created_at (DATETIME) |
| **Relationships** | None (raw stage) |
| **Indexes** | provider, provider_game_id, sport, timestamp |

#### `raw_injuries`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Raw injury reports from data providers. Stores severity, type, and player before normalization. |
| **Columns** | id (INTEGER PK), provider (STRING(50)), player_name (STRING(100)), team_name (STRING(100)), sport (STRING(20)), injury_type (STRING(50)), severity (STRING(20)), description (TEXT), reported_at (DATETIME), raw_json (TEXT), created_at (DATETIME) |
| **Relationships** | None (raw stage) |
| **Indexes** | provider, player_name, team_name, sport, reported_at |

#### `injuries`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Normalized injury data linked to teams and games. Drives feature engineering for the ML model. |
| **Columns** | id (INTEGER PK), player_name (STRING(100)), team_id (FK→teams), sport (STRING(20)), injury_type (STRING(50)), severity (STRING(20)), description (TEXT), reported_at (DATETIME), created_at (DATETIME) |
| **Relationships** | teams (team_id) |
| **Indexes** | team_id, sport, reported_at, severity |

#### `strategies`
| Attribute | Value |
|-----------|-------|
| **Purpose** | User-saved betting strategies. Each strategy is a complete set of parameters for a simulation run. |
| **Columns** | id (INTEGER PK), name (STRING(100)), odds_american (INTEGER), win_probability (FLOAT), bankroll (FLOAT), bet_size (FLOAT), bet_size_type (STRING(20)), num_bets (INTEGER), num_simulations (INTEGER), strategy_type (STRING(20) — single/parlay), created_at (DATETIME), updated_at (DATETIME) |
| **Relationships** | simulation_runs (strategy_id) |
| **Indexes** | name, created_at |

#### `simulation_runs`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Records a single invocation of the Monte Carlo engine. Each run produces many `simulation_results` rows (one per simulation iteration). |
| **Columns** | id (INTEGER PK), strategy_id (FK→strategies, nullable), odds_american (INTEGER), win_probability (FLOAT), bankroll (FLOAT), bet_size (FLOAT), bet_size_type (STRING(20)), num_bets (INTEGER), num_simulations (INTEGER), seed (INTEGER), created_at (DATETIME) |
| **Relationships** | strategies (strategy_id), simulation_results (simulation_run_id), system_play_results (simulation_run_id) |
| **Indexes** | strategy_id, created_at |

#### `simulation_results`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Stores the outcome of each individual simulation iteration (one row per simulation run within a batch). Supports trend analysis and re-computation of metrics. |
| **Columns** | id (INTEGER PK), simulation_run_id (FK→simulation_runs), run_index (INTEGER), final_bankroll (FLOAT), is_profitable (BOOLEAN), max_drawdown (FLOAT), created_at (DATETIME) |
| **Relationships** | simulation_runs (simulation_run_id) |
| **Indexes** | simulation_run_id, run_index, final_bankroll |

#### `system_play_results`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Stores the results of System Plays Engine runs — the calibration report showing stated probability vs. actual win rate. |
| **Columns** | id (INTEGER PK), simulation_run_id (FK→simulation_runs, nullable), stated_probability (FLOAT), actual_win_rate (FLOAT), calibration_error (FLOAT), calibration_status (STRING(50)), confidence_interval_low (FLOAT), confidence_interval_high (FLOAT), recommendation (TEXT), created_at (DATETIME) |
| **Relationships** | simulation_runs (simulation_run_id) |
| **Indexes** | simulation_run_id, calibration_status, created_at |

#### `ml_models`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Model registry. Tracks every trained model version, its training data, performance metrics, and deployment status. |
| **Columns** | id (STRING PK — hash or version string), name (STRING(100)), version (STRING(20)), trained_at (DATETIME), training_dataset (STRING(100)), features_used (JSON), accuracy (FLOAT), calibration_score (FLOAT), roi (FLOAT), cross_validation (JSON), notes (TEXT), is_production (BOOLEAN), is_archived (BOOLEAN), model_path (STRING(255)), created_at (DATETIME) |
| **Relationships** | model_predictions (model_id) |
| **Indexes** | is_production, trained_at, name |

#### `model_predictions`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Stores every prediction made by every model version for every game. Enables backtesting, calibration analysis, and model evaluation. |
| **Columns** | id (INTEGER PK), model_id (FK→ml_models), game_id (FK→games), predicted_probability (FLOAT), confidence (FLOAT), fair_odds_decimal (FLOAT), ev (FLOAT), created_at (DATETIME) |
| **Relationships** | ml_models (model_id), games (game_id) |
| **Indexes** | model_id, game_id, created_at |

#### `backtest_results`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Stores historical backtesting results — the outcome of applying past predictions to actual game results. Feeds into model evaluation and retraining. |
| **Columns** | id (INTEGER PK), model_id (FK→ml_models), game_id (FK→games), predicted_probability (FLOAT), actual_outcome (BOOLEAN), edge (FLOAT), roi (FLOAT), created_at (DATETIME) |
| **Relationships** | ml_models (model_id), games (game_id) |
| **Indexes** | model_id, game_id, created_at |

#### `model_evaluations`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Periodic evaluation of model performance on backtest data. Tracks accuracy, calibration, ROI, and determines when retraining is needed. |
| **Columns** | id (INTEGER PK), model_id (FK→ml_models), evaluated_at (DATETIME), accuracy (FLOAT), calibration_error (FLOAT), avg_roi (FLOAT), brier_score (FLOAT), notes (TEXT), created_at (DATETIME) |
| **Relationships** | ml_models (model_id) |
| **Indexes** | model_id, evaluated_at |

#### `portfolios`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Stores portfolio construction results — the engine's recommended set of bets for a given day, with risk allocation. |
| **Columns** | id (INTEGER PK), date (DATE), total_risk (FLOAT), expected_roi (FLOAT), kelly_exposure (FLOAT), model_id (FK→ml_models, nullable), created_at (DATETIME) |
| **Relationships** | portfolio_items (portfolio_id), ml_models (model_id) |
| **Indexes** | date, model_id |

#### `portfolio_items`
| Attribute | Value |
|-----------|-------|
| **Purpose** | Individual bets within a portfolio. Each item references a game, its prediction, and the recommended bet size/strategy. |
| **Columns** | id (INTEGER PK), portfolio_id (FK→portfolios), game_id (FK→games), model_id (FK→ml_models), confidence_level (STRING(20) — high/medium/low), bet_type (STRING(20) — moneyline/spread/parlay), stake (FLOAT), predicted_probability (FLOAT), ev (FLOAT), recommendation_stars (INTEGER), created_at (DATETIME) |
| **Relationships** | portfolios (portfolio_id), games (game_id), ml_models (model_id) |
| **Indexes** | portfolio_id, game_id, confidence_level

---

## 9. System Plays Engine

### Concept

The System Plays Engine answers: **"Is your probability model actually correct?"**

It works by:
1. Taking a stated probability (from user input for MVP, ML model in future)
2. Running 1,000+ simulations using that probability
3. Comparing the **stated probability** vs. the **actual win rate** in simulations
4. Reporting the **calibration error** — the gap between stated and actual

### How It Works

```
Model says:  "60% chance Team A wins"
             │
             ▼
  Simulate 1,000 runs at 60% win rate
             │
             ▼
   Actual win rate: 59.8%  (expected: ~60%)
             │
             ▼
  Calibration error: 0.2% → "Your model is well-calibrated"
```

### Calibration Bands

For a well-calibrated model, the actual win rate should match the stated probability within statistical tolerance:

| Stated Prob | Expected Actual (±) | Calibration Status |
|-------------|---------------------|-------------------|
| 55% | 52%–58% | Good |
| 60% | 57%–63% | Good |
| 65% | 62%–68% | Good |
| 70% | 67%–73% | Good |

If the actual win rate falls outside the tolerance band, the model is **miscalibrated**:
- **Overconfident:** Actual < Stated (model overestimates probability)
- **Underconfident:** Actual > Stated (model underestimates probability)

### MVP Behavior

In the MVP, the "model" is the user. The user inputs their estimated probability. The System Plays Engine runs simulations using that probability. The actual win rate should closely match the stated probability (since the simulation uses the same probability). The value here is **educational**: it shows users how variance affects small sample sizes, and teaches them that their stated confidence level should match reality over thousands of bets.

### API: POST `/api/system-plays`

**Request:**
```json
{
  "odds_american": -110,
  "win_probability": 0.60,
  "bankroll": 1000,
  "bet_size": 100,
  "num_bets": 100,
  "num_simulations": 10000,
  "seed": 42
}
```

**Response:**
```json
{
  "stated_probability": 0.60,
  "actual_win_rate": 0.5987,
  "calibration_error": 0.0013,
  "calibration_status": "well_calibrated",
  "confidence_interval": [0.58, 0.62],
  "metrics": { ... },
  "distribution": { ... },
  "recommendation": "Your probability estimates are well-calibrated. Keep tracking."
}
```

---

## 10. Data Collection Pipeline

### Architecture

```
┌─────────────┐  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐  ┌────────────┐
│  Providers  │  │  Collectors  │  │ Validation  │  │ Normalizer   │  │ Raw Tables │
└──────┬──────┘  └──────┬───────┘  └─────┬───────┘  └──────┬───────┘  └─────┬──────┘
       │                 │                 │                  │                │
┌──────┴──────┐          │          ┌──────┴──────┐          │       ┌────────┴────────┐
│ TheOddsAPI  │──────────┤          │ JSON schema │          │       │ raw_odds          │
│ OddsJam     │          │          │ validation  │          │       │ raw_injuries      │
│ OpticOdds   │          │          │ retry logic │          │       │ raw_teams         │
│ ESPN        │──────────┘          │ duplicate   │          │       └────────┬────────┘
│ Manual CSV  │                      │ detection   │          │                │
└─────────────┘                      └──────┬──────┘          │       ┌────────┴────────┐
                                           │                   │       │ games           │
                                           ▼                   │       │ game_odds       │
                                   ┌────────────┐             │       │ injuries        │
                                   │ Scheduler  │             │       │ teams           │
                                   │ (30 min)   │             │       └────────┬────────┘
                                   └─────┬──────┘             │                │
                                         │                    │       ┌────────┴────────┐
                                         ▼                    │       │ Feature Pipeline │
                              ┌─────────────────┐            │       │ (FeatureService)  │
                              │  Cache          │            │       │                   │
                              │  (in-memory)    │            │       │ → model_features  │
                              └─────────────────┘            │       └────────┬────────┘
                                                             │                │
                                                             │       ┌────────┴────────┐
                                                             │       │ model_predictions │
                                                             │       │ ml_models         │
                                                             │       │ backtest_results  │
                                                             │       │ model_evaluations │
                                                             │       └─────────────────┘
                                                             │
                                                             ▼
                                              ┌─────────────────────────┐
                                              │  RecommendationService  │
                                              │  → system_play_results  │
                                              │  → portfolios           │
                                              │  → portfolio_items      │
                                              └─────────────────────────┘
```

### Collector Interface

Each data provider has a collector that implements a standard interface:

```python
class BaseCollector(ABC):
    @abstractmethod
    async def fetch(self, sport: str) -> list[dict]:
        """Fetch raw data from provider. Returns list of raw records."""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return unique provider name."""
        pass

class TheOddsApiCollector(BaseCollector):
    async def fetch(self, sport: str) -> list[dict]:
        """Fetches odds from TheOddsAPI, returns raw JSON."""
        ...
        return raw_odds_records

class OddsJamCollector(BaseCollector):
    async def fetch(self, sport: str) -> list[dict]:
        """Fetches odds + injury data from OddsJam."""
        ...
```

### Pipeline Stages

#### 1. Collect
- Each collector fetches data from its provider
- Results saved as raw JSON in the corresponding `raw_*` table
- Timestamped for freshness

#### 2. Validate
- JSON schema validation (Pydantic models)
- Required fields: game_id, teams, odds, timestamp
- Retry with exponential backoff (max 3 retries)
- Failed imports logged to `collection_errors` table

#### 3. Normalize
- Map provider-specific fields to canonical schema
- Deduplicate: if same game_id + market + timestamp exists, skip
- Convert odds to American format (canonical)
- Calculate implied probability + no-vig fair odds

#### 4. Raw Tables
- `raw_odds`: unprocessed odds from all providers
- `raw_injuries`: unprocessed injury reports
- `raw_teams`: unprocessed team data

#### 5. Feature Pipeline
- `FeatureService.extract_features()` transforms raw tables + normalized tables into model-ready feature vectors
- Runs synchronously when a prediction is needed
- Caches results in-memory for 15 minutes

### Provider Priority & Retry Logic

| Priority | Provider | Data | Retry | Fallback |
|----------|----------|------|-------|----------|
| 1 | TheOddsAPI | Odds | 3 retries, 2s backoff | None (MVP) |
| 2 | OddsJam | Odds + injuries | 3 retries, 5s backoff | TheOddsAPI |
| 3 | OpticOdds | Injuries | 2 retries, 3s backoff | OddsJam |
| 4 | Manual CSV | Anything | N/A | All providers |

### Refresh Schedule

| Data | Refresh | Trigger |
|------|---------|---------|
| Today's games + odds | Every 30 min (active) | Scheduler background task |
| Injury reports | Every 60 min | Scheduler background task |
| Historical data | Daily (2 AM local) | Scheduler background task |
| Model retraining | Weekly (Sunday) | Scheduler background task |

### Failed Import Handling

- Failed imports are logged to `collection_errors` table (provider, url, error, timestamp)
- Errors older than 30 days are auto-purged
- Dashboard shows "Data Sources" page with provider health status
- If a provider fails 3 consecutive times, an alert is logged

### Data Sources

| Provider | Free Tier | Data | Used For (Sprint) |
|----------|-----------|------|-------------------|
| **TheOddsAPI** | 25 req/day, NBA+MLB | Live odds, moneyline/spreads/totals | Base odds source (Sprint 9) |
| **OddsJam** | Paid | Injury data, line movement, historical | Injury data + line movement (future) |
| **OpticOdds** | Paid | Injury reports, schedules | Injury data (future) |
| **MoneyLine API** | Free tier | Full stats + odds + injuries | Comprehensive data (future) |

### TheOddsAPI Integration

**Endpoint:** `GET /v1/odds?sport_key={sport}&markets=h2h,spreads`

**Response structure:**
```json
[
  {
    "id": "game-id-123",
    "sport_key": "americanfootball_nfl",
    "commence_time": 1234567890,
    "home_team": "Kansas City Chiefs",
    "away_team": "Buffalo Bills",
    "bookmakers": [
      {
        "key": "draftkings",
        "title": "DraftKings",
        "last_update": "2026-01-01T12:00:00Z",
        "markets": [
          {
            "key": "h2h",
            "outcomes": [
              {"name": "Kansas City Chiefs", "price": -150},
              {"name": "Buffalo Bills", "price": 130}
            ]
          }
        ]
      }
    ]
  }
]
```

### Cache Strategy

- **In-memory cache:** Store today's games + odds, refresh every 15 minutes
- **SQLite persistence:** Store all fetched odds for historical analysis (future)
- **Stale threshold:** If odds are older than 2 hours, show "Stale" badge in UI

### Future Data Enrichment (Not in MVP)

| Data Point | Source | Purpose for Probability |
|-----------|--------|------------------------|
| Player injuries | OddsJam / OpticOdds | Adjust win probability |
| Line movement | OddsJam | Detect sharp vs. public betting |
| Team ATS record | Sports data API | Historical edge |
| Player age/form | Sports reference | Performance trends |
| Weight cuts (MMA) | MMA-specific API | Fight probability adjustment |
| Weather | Weather API | Outdoor sport impact |

---

## 11. ML Pipeline

### Model Interface

```python
from abc import ABC, abstractmethod
from .features import FeatureVector

class ProbabilityModel(ABC):
    @abstractmethod
    def predict(self, features: FeatureVector) -> float:
        """Returns probability 0.0–1.0"""
        pass
    
    @abstractmethod
    def get_confidence(self, features: FeatureVector) -> float:
        """Returns confidence 0.0–1.0"""
        pass

class UserInputModel(ProbabilityModel):
    """MVP: wraps a user-provided probability. Always returns it."""
    def __init__(self, probability: float):
        self.probability = probability
    
    def predict(self, features: FeatureVector) -> float:
        return self.probability
    
    def get_confidence(self, features: FeatureVector) -> float:
        return 1.0  # User is 100% confident in their own input

class StubModel(ProbabilityModel):
    """Testing: returns random probability around a base value."""
    def predict(self, features: FeatureVector) -> float:
        return np.random.default_rng().uniform(0.45, 0.55)
```

### Feature Schema (Sprint 13)

| Feature | Source | Type | Description |
|---------|--------|------|-------------|
| `decimal_odds` | TheOddsAPI | float | e.g., 1.909 |
| `implied_probability` | Calculated | float | No-vig implied probability |
| `line_movement_pct` | OddsJam | float | % change in line over 24h |
| `is_home` | Games data | bool | Home team advantage |
| `rest_days` | Schedule | int | Days since last game |
| `injury_count` | Injury reports | int | Key players injured |
| `avg_injury_severity` | Injury reports | float | 0.0–1.0 |
| `team_win_pct` | Historical | float | Season win rate |
| `historical_h2h` | Historical | float | Head-to-head record |
| `player_form` | Stats | float | Recent performance index |

### Training Pipeline (Stub)

```python
# backend/ml/pipeline.py
class TrainingPipeline:
    def __init__(self):
        self.model = LogisticRegression()
        self.feature_scaler = StandardScaler()
        self.feature_names = None
    
    def prepare_training_data(self) -> tuple[np.ndarray, np.ndarray]:
        """Load historical game results + features. Not implemented in MVP."""
        raise NotImplementedError("Training data pipeline not available yet")
    
    def train(self) -> dict:
        """Train the model. Not implemented in MVP."""
        raise NotImplementedError("Model training not available yet")
    
    def save(self, path: str) -> None:
        """Save model artifact. Not implemented in MVP."""
        raise NotImplementedError
```

### Model Versioning (Future)

> **See Section 14: Model Registry** for the complete model versioning specification. This subsection is a brief summary.

Full model versioning with registry, promotion criteria, and deployment status is defined in [Section 14 — Model Registry](#14-model-registry).

---

## 12. Service Responsibilities

Each service has a single responsibility and owns a specific domain. This separation makes the codebase navigable for AI agents and human developers alike.

| Service | Location | Responsibility | Key Methods |
|---------|----------|----------------|-------------|
| **SimulationService** | `backend/simulation/` | Pure Monte Carlo simulation logic. No database, no API. | `simulate_once()`, `simulate_batch()`, `calculate_metrics()`, `simulate_parlay()` |
| **BankrollService** | `backend/simulation/bankroll.py` | Bankroll strategy calculations (flat, percentage, Kelly, half-Kelly). | `calculate_stake()`, `kelly_criterion()`, `half_kelly_fraction()` |
| **OddsService** | `backend/simulation/odds.py` | Odds conversion and fair-odds calculation. | `american_to_decimal()`, `american_to_implied_prob()`, `remove_vig()` |
| **PredictionService** | `backend/ml/models/` | Wraps the active probability model. Returns predictions + confidence. | `predict(game_features)`, `get_confidence()`, `predict_batch()` |
| **FeatureService** | `backend/ml/features/` | Extracts and transforms raw data into model features. | `extract_features()`, `normalize_features()`, `validate_features()` |
| **DataCollectionService** | `backend/services/` | Fetches, validates, and normalizes data from external providers. | `collect_odds()`, `collect_injuries()`, `normalize_game()` |
| **BacktestService** | `backend/ml/backtest.py` | Historical replay: applies past predictions to actual results. | `run_backtest()`, `evaluate_model()`, `generate_evaluation()` |
| **RecommendationService** | `backend/ml/recommend.py` | Creates System Plays from model predictions + simulation results. | `generate_recommendation()`, `calculate_intelligence_score()`, `build_portfolio()` |
| **StorageService** | `backend/crud/` | All database read/write operations. | `save_strategy()`, `save_simulation_run()`, `save_model_prediction()` |
| **SchedulerService** | `backend/services/scheduler.py` | Background task for periodic data collection and model retraining. | `schedule_odds_collection()`, `schedule_backtest()`, `schedule_retrain()` |

### Service Invocation Order

```
DataCollectionService (periodically)
    → FeatureService (on-demand)
    → PredictionService (on-demand)
    → RecommendationService
        → SimulationService (Monte Carlo)
        → BankrollService (stake sizing)
        → BacktestService (validation, if historical)
    → StorageService (persist results)
```

---

## 13. Recommendation Lifecycle

The complete pipeline from raw data ingestion to model evaluation and retraining. This is the heartbeat of the system.

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐
│ Game Imported   │────▶│ Features         │────▶│ Prediction   │
│ (Data Collector)│     │ Generated        │     │ (ML Model)   │
└─────────────────┘     └────────┬─────────┘     └──────┬───────┘
                                 │                        │
                                 ▼                        ▼
                        ┌──────────────────┐     ┌────────────────┐
                        │ Simulation       │     │ EV Calculation │
                        │ (Monte Carlo)    │     │ (Bankroll)     │
                        └────────┬─────────┘     └──────┬─────────┘
                                 │                        │
                                 ▼                        ▼
                        ┌─────────────────────────────────────────┐
                        │       System Play                     │
                        │  (RecommendationService creates the    │
                        │   final recommendation with score)    │
                        └──────────────────┬────────────────────┘
                                           │
                                           ▼
                                ┌─────────────────┐
                                │  User Views     │
                                │  Recommendation │
                                └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  Game Ends      │
                                │  (result stored)│
                                └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  Backtest       │
                                │  Database       │
                                │  (results stored)│
                                └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  Model          │
                                │  Evaluation     │
                                │  (calibration,  │
                                │   ROI, accuracy)│
                                └────────┬────────┘
                                         │
                                         ▼
                                ┌─────────────────┐
                                │  Retraining     │
                                │  Trigger (if    │
                                │  performance    │
                                │  degrades)      │
                                └─────────────────┘
```

### Lifecycle Stages

| Stage | Service | Input | Output | Storage |
|-------|---------|-------|--------|---------|
| 1. Game Imported | DataCollectionService | API response from TheOddsAPI | Normalized game record | `games`, `game_odds`, `raw_odds` |
| 2. Features Generated | FeatureService | Game + odds + injuries | Feature vector (30+ features) | `features` (in-memory, not persisted yet) |
| 3. Prediction | PredictionService | Feature vector | Probability + confidence | `model_predictions` |
| 4. Simulation | SimulationService | Odds + probability + bankroll params | Monte Carlo results | `simulation_runs`, `simulation_results` |
| 5. EV Calculation | BankrollService | Simulation results | EV, risk metrics | `simulation_runs` (enriched) |
| 6. System Play | RecommendationService | Prediction + simulation + EV | Final recommendation with score | `system_play_results` |
| 7. User Views | Frontend | Recommendation | User feedback (optional) | `user_actions` (future) |
| 8. Game Ends | DataCollectionService | API game result | Actual outcome | `games` (updated with score) |
| 9. Backtest | BacktestService | Actual outcome + prediction | Backtest result | `backtest_results` |
| 10. Model Evaluation | BacktestService | All backtest results | Performance metrics | `model_evaluations` |
| 11. Retraining | SchedulerService | Model evaluation + data | New model version | `ml_models` (new row) |

---

## 14. Model Registry

### Schema

| Field | Type | Description |
|-------|------|-------------|
| id | STRING PK | Unique identifier (git commit hash or UUID) |
| name | STRING(100) | Human-readable name (e.g., "NFL v3 LogisticRegression") |
| version | STRING(20) | SemVer (e.g., "3.2.1") |
| trained_at | DATETIME | When training completed |
| training_dataset | STRING(100) | Dataset name/version used for training |
| features_used | JSON | List of feature names the model was trained on |
| accuracy | FLOAT | Backtest accuracy score |
| calibration_score | FLOAT | How well-calibrated (0–1, lower = better calibrated) |
| roi | FLOAT | Backtest ROI percentage |
| cross_validation | JSON | K-fold CV results (mean, std, fold_scores) |
| notes | TEXT | Free-form notes about training |
| is_production | BOOLEAN | Whether this is the active model |
| is_archived | BOOLEAN | Retired models kept for analysis |
| model_path | STRING(255) | Filesystem path to model artifact |
| created_at | DATETIME | Record creation timestamp |

### Versioning Rules

1. **One production model at a time** — `is_production = TRUE` is unique per sport
2. **New model doesn't become production automatically** — must pass backtest threshold
3. **Archived models are never deleted** — kept for A/B comparison
4. **Version strings follow SemVer** — major.minor.patch
5. **Training dataset is versioned** — same features but different data is a new version

### Promotion Criteria

A model is promoted to `is_production = TRUE` when:
- Backtest ROI > 0 for at least 500 games
- Calibration score < 0.05 (5% deviation from stated probability)
- Accuracy > historical baseline by at least 2%

---

## 15. Explainability

### Output Format

Every recommendation includes an explainability breakdown so users understand WHY a bet was suggested:

```json
{
  "recommendation": "Boston Bruins ML",
  "confidence": "73%",
  "top_factors": [
    {"factor": "Home Advantage", "direction": "positive", "weight": 0.18},
    {"factor": "Opponent Back-to-back", "direction": "positive", "weight": 0.12},
    {"factor": "Better Offensive Rating", "direction": "positive", "weight": 0.09},
    {"factor": "Better Net Rating", "direction": "positive", "weight": 0.07},
    {"factor": "Cold Goaltender", "direction": "negative", "weight": -0.05}
  ],
  "simulation_result": "81%",
  "ev": "+8.3%",
  "explanation": "Boston is at home (home teams win 55% in NHL). Opponent played last night (back-to-back penalty). Boston's offensive rating is 8.2% above league average."
}
```

### Factor Weights

Factor weights come from the model's feature importance (e.g., SHAP values for tree-based models, coefficients for logistic regression). The top 5 factors by absolute weight are displayed.

| Direction | Meaning |
|-----------|---------|
| Positive (+) | Increases probability of the recommended outcome |
| Negative (-) | Decreases probability of the recommended outcome |

### MVP Explainability

For the MVP (user-input probability), the explainability output is simpler:
```
"Your estimate: 58%. Implied probability from odds: 52.4%. Your edge: +5.6%."
```

This tells the user: "You think this hits 58% of the time, but the sportsbook prices it at 52.4%. You have a 5.6% edge."

---

## 16. Intelligence Score

### Concept

Every recommendation gets an **Intelligence Score** — an overall rating (0–100) that aggregates probability, simulation confidence, EV, and model confidence. This is SIP's unique differentiator instead of simply saying "Bet this."

### Score Components

| Component | Weight | Calculation | Example |
|-----------|--------|-------------|---------|
| **Probability** | 25% | Predicted probability from model | 74% → 18.5 points |
| **Simulation** | 25% | Win rate in Monte Carlo simulation | 81% → 20.3 points |
| **Expected Value** | 25% | EV vs. sportsbook line | +8.3% → 20.8 points |
| **Model Confidence** | 15% | Model's self-reported confidence | 88% → 13.2 points |
| **Calibration** | 10% | How well model matches historical accuracy | Well-calibrated → 10 points |

### Example Score

```
Overall Intelligence: 92/100

  Probability        74%    ████████████████░░  (18.5/25)
  Simulation         81%    ██████████████████  (20.3/25)
  Expected Value    +8.3%   ██████████████████  (20.8/25)
  Model Confidence  88%    ███████████████     (13.2/15)
  Calibration     Good   ██████████          (10.0/10)

Recommendation: ★★★★☆  (Strong play, low risk)
Risk Level: Low (Risk of ruin < 10% in simulations)
```

### Risk Levels

| Score Range | Risk Level | Stars | Description |
|-------------|------------|-------|-------------|
| 85–100 | Low | ★★★★★ | Strong play, highly recommended |
| 70–84 | Medium | ★★★★☆ | Solid play, moderate risk |
| 55–69 | High | ★★★☆☆ | Speculative, high variance |
| 40–54 | Very High | ★★☆☆☆ | Avoid unless desperate |
| 0–39 | Extreme | ☆☆☆☆☆ | Do not bet |

### How the Score is Calculated

```
intelligence_score = (
    probability_score * 0.25 +
    simulation_score * 0.25 +
    ev_score * 0.25 +
    confidence_score * 0.15 +
    calibration_score * 0.10
)

Where:
  probability_score = predicted_probability * 25
  simulation_score = (simulation_win_rate / max_stated_prob) * 25
  ev_score = sigmoid(ev_percentage) * 25  # maps -50% to +50% → 0 to 25
  confidence_score = model_confidence * 15
  calibration_score = (1 - calibration_error) * 10
```

---

## 17. Portfolio Construction

Instead of recommending individual bets, the engine constructs a **daily portfolio** of bets with risk allocation across confidence levels.

### Portfolio Algorithm

1. **Filter** all games with model predictions today
2. **Rank** by Intelligence Score (descending)
3. **Allocate** by confidence band:
   - **High Confidence** (Score 85+): 2 bets, 40% of total bankroll
   - **Medium Confidence** (Score 70–84): 4 bets, 30% of total bankroll
   - **Long Shot** (Score 55–69): 6 bets, 20% of total bankroll
   - **Avoid** (Score < 55): Do not include
4. **Calculate per-bet stake** using Kelly Criterion
5. **Cap total exposure** at 80% of bankroll (leaves 20% buffer)

### Example Portfolio

```
Today's Portfolio — 2026-01-15

  Confidence Level  | Bets | Allocation | Expected ROI
  -----------------------------------------------
  High (85+)        | 2    | 40%        | 12.0%
  Medium (70-84)    | 4    | 30%        | 8.0%
  Long Shot (55-69) | 6    | 20%        | 4.0%
  -----------------------------------------------
  Total             | 12   | 90%        | 8.0%

  Key Metrics:
  Total Risk:     6%
  Expected ROI:   8%
  Kelly Exposure: 12%
  Max Drawdown:  -15% (from simulations)
```

### Portfolio Fields (`portfolios` table)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | |
| date | DATE | Day the portfolio is for |
| total_risk | FLOAT | % of bankroll at risk |
| expected_roi | FLOAT | Weighted average ROI |
| kelly_exposure | FLOAT | % of bankroll allocated per Kelly |
| model_id | FK→ml_models | Which model generated the portfolio |
| created_at | DATETIME | |

### Portfolio Item Fields (`portfolio_items` table)

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER PK | |
| portfolio_id | FK→portfolios | |
| game_id | FK→games | |
| confidence_level | STRING(20) | high/medium/low |
| bet_type | STRING(20) | moneyline/spread/parlay |
| stake | FLOAT | Dollar amount |
| predicted_probability | FLOAT | From model |
| ev | FLOAT | Expected value |
| recommendation_stars | INTEGER | 1–5 |
| created_at | DATETIME | |

---

## 18. AI Agent Guide

This document is designed to be executed by AI agents. These rules ensure consistency and quality.

### Never

- **Rename folders** without updating all imports and the folder structure doc
- **Change architecture** mid-sprint (database schema, API contracts, service boundaries)
- **Implement a future sprint's functionality** in the current sprint
- **Skip tests** — every backend function and frontend component must have test coverage
- **Change database schema** without documenting the migration (create a migration file)
- **Hardcode API keys** — use environment variables via `config.py`
- **Mix concerns** — SimulationService must not touch the database; StorageService must not run simulations
- **Write code that bypasses the service layer** — always go through the defined services
- **Add dependencies** without updating `requirements.txt` / `package.json`

### Always

- **Complete one sprint before starting the next** — verify all acceptance criteria
- **Run lint before committing** — `ruff check backend/` + `eslint frontend/src/`
- **Run tests before finishing a sprint** — `pytest backend/tests/` + `vitest frontend/src/`
- **Update this documentation** when you make a change
- **Write tests first** (TDD) for new backend functions
- **Commit with a sprint-scoped message** — e.g., `Sprint 6: Add simulation form component`
- **Verify the running app** — open Electron and manually test the feature
- **Stop at end of sprint** — do not continue to next sprint without explicit approval

### Sprint Execution Contract

Each sprint must deliver:
1. **Working code** — the feature works end-to-end in the running app
2. **Tests** — unit tests for logic, integration tests for API
3. **Documentation** — updated Technical Spec, if relevant
4. **Verification** — manual QA checklist completed

An agent should **stop and report** when:
- A test fails that cannot be fixed in one iteration
- The running app does not work as expected
- A backend/frontend integration issue is discovered
- The scope of the current sprint has been exceeded

---

## 19. Design Decisions

### 1. Why Electron + FastAPI instead of pure browser React?

| Factor | Browser-only | Electron + FastAPI | Why chose this |
|--------|-------------|---------------------|----------------|
| **ML integration** | Impossible in browser | Native Python | Future ML models need Python libs |
| **Data storage** | LocalStorage (limited) | SQLite (robust) | Strategies, odds, results need real DB |
| **Performance** | Limited by JS | Full CPU power | Simulations benefit from NumPy |
| **Packaging** | Just a URL | Installable app | Desktop app feels professional |
| **API keys** | Exposed to user | Server-side | TheOddsAPI keys stay secure |

### 2. Why NumPy for simulation?

The Monte Carlo simulation's bottleneck is random number generation (RNG). NumPy's `default_rng` generates arrays of random numbers orders of magnitude faster than Python's `random` module. For 1,000 simulations × 100 bets = 100K random draws, NumPy takes ~5ms vs. Python's ~50ms.

### 3. Why store trajectories in SQLite?

Trajectories are needed for the bankroll chart. Storing them allows:
- Chart rendering without re-simulating
- "View previous simulation" feature
- Exporting trajectories for analysis

We store only summary statistics (percentiles) to avoid bloating the DB.

### 4. Why separate System Plays from plain Simulation?

The System Plays Engine answers a different question: **"Is my model calibrated?"** A plain simulation answers **"What happens if I bet this way?"** The System Plays Engine adds a calibration comparison layer, which is the educational feedback loop.

### 5. Why SQLite instead of PostgreSQL?

| Factor | SQLite | PostgreSQL |
|--------|--------|------------|
| Setup | No server needed | Requires server |
| Performance | Fast for <10K records | Better for >100K records |
| Local-first | Native | Requires config |
| MVP scope | Sufficient | Overkill |

SQLite is the right choice for a local-first desktop app. Can migrate to PostgreSQL if cloud sync is added later.

### 6. Why TheOddsAPI over other odds providers?

| Provider | Free Tier | API Simplicity | Coverage |
|----------|-----------|----------------|----------|
| **TheOddsAPI** | 25 req/day | Simple REST | 26 sports, 50 books |
| OddsJam | None | Complex | More data points |
| OpticOdds | None | Complex | Best injury data |
| Betstamp | None | Complex | Best for live odds |

TheOddsAPI is the best starting point — free tier allows development, simple REST API, broad sports coverage.

### 7. Why not use scikit-learn in MVP?

scikit-learn would be ideal for the ML model, but:
- The MVP uses user-input probability (no ML model yet)
- scikit-learn adds 200+ MB to the install size
- The `ProbabilityModel` interface is designed to accept any sklearn model later
- We use `numpy` (much smaller) for simulation, which is sufficient

### 9. Why 15 sprints?

The sprint plan covers MVP + the transition to data-driven features:
- Sprints 0–8: Core MVP (simulation, API, UI, charts, strategies)
- Sprints 9–11: Data integration + differentiators (System Plays, Parlay, Bankroll)
- Sprints 12–14: ML pipeline, backtesting, Intelligence Score & Portfolio

Beyond Sprint 14 would be actual ML model training, which requires historical data collection and weeks of model development.

### 9. Why not support all sports from day one?

TheOddsAPI covers the same endpoints across all sports. But:
- Different sports have different betting markets (point spreads, totals, moneyline)
- MMA has unique factors (weight cuts, fights canceled at weigh-in)
- Each sport needs its own feature schema and model

We start with NFL/NBA (most popular US sports, best data coverage) and add others incrementally.
