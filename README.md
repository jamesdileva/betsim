# Betsim

Monte Carlo betting simulator — a local-first desktop app (Electron + FastAPI + SQLite) that helps bettors understand risk, variance, and edge through simulation. It does not predict winners.

## Tech Stack

- **Frontend:** Electron + React 18 + TypeScript + Vite
- **Backend:** FastAPI (Python) + SQLAlchemy 2.0 + NumPy
- **Database:** SQLite at `~/.betsim/betsim.db`

## Getting Started

Requirements: Node 20+, Python 3.11+.

```bash
# one-time setup: create venv, install python deps, install frontend deps
npm run setup

# start backend (uvicorn), vite dev server, and electron together
npm run dev
```

The Electron window shows the backend connection status (`GET /health`).

## Scripts (root)

| Script | What it does |
|--------|--------------|
| `npm run setup` | Create `.venv`, install backend + frontend dependencies |
| `npm run dev` | Backend + Vite + Electron concurrently |
| `npm test` | Backend pytest + frontend vitest |
| `npm run lint` | ruff (backend) + eslint (frontend) |
| `npm run build` | Production frontend build (Vite) |

## Project Structure

- `backend/` — FastAPI app, SQLAlchemy models, simulation engine (see `docs/02_Technical_Specification.md`)
- `frontend/` — React + Electron app
- `docs/` — sprint plan, technical spec, product design

## Documentation

- [Sprint Plan](docs/01_Sprint_Plan.md)
- [Technical Specification](docs/02_Technical_Specification.md)
- [Product Design](docs/03_Product_Design.md)
- [AGENTS.md](AGENTS.md) — working history / changelog
