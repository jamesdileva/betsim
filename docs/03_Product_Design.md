# Betsim — Product Design

**Project:** Betsim - Monte Carlo Betting Simulator  
**Version:** 1.0  
**Last Updated:** 2026-08-01

---

## Table of Contents

1. [Product Vision & Positioning](#1-product-vision--positioning)
2. [Feature Priority Matrix](#2-feature-priority-matrix)
3. [Navigation Structure](#3-navigation-structure)
4. [UI Workflows](#4-ui-workflows)
5. [Screen Designs](#5-screen-designs)
6. [Component Library](#6-component-library)
7. [Design Principles](#7-design-principles)
8. [MVP Feature Checklist](#8-mvp-feature-checklist)
9. [Intelligence Score](#9-intelligence-score)
10. [Portfolio Construction](#10-portfolio-construction)

---

## 1. Product Vision & Positioning

### Core Value Proposition

> **Don't tell me what to bet. Show me what happens if I do.**

Betsim is a Monte Carlo betting simulator that helps bettors understand risk, variance, and edge through simulation. It does NOT predict winners — it runs 1,000–100,000 simulations of a betting strategy and shows the statistical outcomes.

### Positioning

| Aspect | Betsim | Typical Betting Tools |
|--------|--------|----------------------|
| **Claim** | "Here's your risk of ruin" | "Bet this winner!" |
| **Method** | Monte Carlo simulation | Prediction algorithms |
| **Output** | Probability distributions | Pick recommendations |
| **Goal** | Education + risk management | Profit prediction |

### Key Messaging

- "You can win 55% of bets and still go broke."
- "Your strategy only profits long term if edge > X%."
- "Simulations don't lie — variance destroys bad bankroll strategies."

---

## 2. Feature Priority Matrix

| Feature | Priority | Sprint | Why |
|---------|----------|--------|-----|
| **Run simulation** (odds, prob, bankroll, bet size) | P0 | 6 | Core function |
| **Results: win %, EV, risk of ruin** | P0 | 6 | Primary output |
| **Bankroll trajectory chart** | P0 | 7 | Visual risk understanding |
| **Distribution histogram** | P0 | 7 | Shows variance |
| **Save/load strategies** | P0 | 8 | Reuse without re-typing |
| **Dark mode only** | P0 | 6 | Eye comfort for nighttime use |
| **Onboarding tutorial** | P0 | 6 | First 5 min determines retention |
| **System Plays Engine** (model calibration) | P1 | 10 | Key differentiator |
| **Scenario Library** | P1 | 8 | Immediate "wow" — load & simulate instantly |
| **Simulation History** | P1 | 8 | Track betting decisions over time |
| **Intelligence Score** | P1 | 14 | Unique scoring per recommendation |
| **Parlay simulator** | P1 | 11 | High-value feature |
| **Side-by-side Strategy Comparison** | P1 | 11 | Compare Flat vs Kelly vs Parlay on same chart |
| **Portfolio Construction** | P1 | 14 | Portfolio theory for betting |
| **Settings / Preferences** | P1 | 6 | Default sim count, API keys, storage |
| **Live odds integration** | P1 | 9 | Reduces manual input |
| **ML pipeline infrastructure** | P2 | 13 | Future extension |
| **Strategy comparison** (single) | P2 | Future | Advanced analysis |
| **Explainability** (top factors) | P2 | 13 | User trust |
| **Export to CSV** | P2 | 8 | Data portability |
| **Multiple sports** | P2 | Future | Market expansion |

---

## 3. Navigation Structure

```
Betsim Desktop App
│
├── 🏠 Simulation Workspace  ← Default page (Sprint 6)
│   ├── Input form (with live odds selector)
│   ├── Scenario templates
│   ├── Run simulation
│   └── Results: metrics + charts
│
├── 📊 Results History        (Sprint 8)
│   ├── Past simulations list
│   ├── Filter by date/sport
│   └── Re-run or export
│
├── 🎯 System Plays           (Sprint 10)
│   ├── Model calibration
│   ├── Stated vs. actual probability
│   └── Calibration report
│
├── 🔄 Parlay Simulator       (Sprint 11)
│   ├── Parlay builder
│   ├── Combined probability
│   └── Variance analysis
│
├── 💼 Portfolio              (Sprint 14)
│   ├── Today's picks (confidence bands)
│   ├── Risk allocation
│   └── Export portfolio
│
├── 💾 Strategies             (Sprint 8)
│   ├── Saved strategies
│   ├── Create/edit
│   └── Run from saved
│
├── 🎮 Onboarding             (Sprint 6)
│   ├── First-run tutorial
│   └── Interactive walkthrough
│
└── ⚙️ Settings               (Sprint 6)
    ├── Default simulation count
    ├── Dark mode toggle
    ├── API keys
    └── Data storage location
```

### Navigation Bar

```
[ Betsim logo ]  Simulation Workspace | System Plays | Parlay Simulator | Strategies | Settings
              [User avatar]
```

---

## 4. UI Workflows

### Workflow 1: Run a Basic Simulation (MVP)

```
1. User opens Betsim → lands on Simulation Workspace
2. User fills in:
   - Odds: -110 (with implied probability helper: 52.38%)
   - Win probability: 55% (user's estimate)
   - Bankroll: $1,000
   - Bet size: $50 (flat) or 5% (percentage)
   - Number of bets: 100
   - Number of simulations: 5,000 (default)
3. User clicks "Run Simulation"
4. Loading spinner (API processes)
5. Results appear:
   - Metric cards: Win % 62%, Avg Bankroll $1,240, Risk of Ruin 18%, EV $2.27/bet
   - Bankroll trajectory chart (median line + percentiles)
   - Distribution histogram (final bankroll spread)
6. User can:
   - Click "Save Strategy" to save these params
   - Adjust params and re-run
   - Export results as CSV
```

### Workflow 2: Save and Reuse a Strategy

```
1. From Simulation Workspace results → click "Save Strategy"
2. Enter strategy name (e.g., "NFL Week 1 -5")
3. Strategy appears on Strategies page
4. On Strategies page → click strategy card → "Run Simulation"
5. Results load with saved params
6. Can edit strategy (updates saved version)
```

### Workflow 3: System Plays Engine

```
1. User navigates to System Plays
2. Inputs:
   - Odds: -110
   - Model probability: 60% (what the model/you says)
   - Bankroll: $1,000
   - Bet size: 2% of bankroll
   - Number of bets: 100
   - Simulations: 10,000
3. Click "Calibrate Model"
4. Results:
   - Stated probability: 60%
   - Actual win rate (from simulations): 59.9%
   - Calibration error: 0.1%
   - Status: "Well calibrated"
   - Recommendation: "Your model is accurate. Run more bets to refine."
5. If miscalibrated (e.g., states 70% but actual is 60%):
   - Status: "Overconfident"
   - Recommendation: "Your model overestimates probability by 10%. Consider adjusting."
```

### Workflow 4: Parlay Simulator

```
1. User navigates to Parlay Simulator
2. Adds 3 selections:
   - Leg 1: -110 odds, 55% win prob
   - Leg 2: -110 odds, 55% win prob
   - Leg 3: +150 odds, 40% win prob
3. Combined probability: 0.55 × 0.55 × 0.40 = 12.1%
4. Combined payout: 1.909 × 1.909 × 2.500 = 9.07x
5. EV calculation: 12.1% × (9.07 - 1) - 87.9% × 1 = -0.26 → -26% EV
6. Click "Simulate Parlay" → 5,000 runs
7. Results show:
   - Actual win rate: ~12%
   - Risk of ruin: 95%+
   - "This parlay has negative EV. You need >X% edge on each leg to break even."
```

### Workflow 5: Bankroll Strategy Comparison

```
1. User runs a simulation with "Flat" strategy ($50/bet)
2. Results show: Risk of ruin 18%, avg bankroll $1,240
3. User switches to "Kelly" strategy
4. App shows: "Kelly recommends 4.5% of bankroll"
5. User re-runs → Results show: Risk of ruin 34%, avg bankroll $1,420
6. Side-by-side comparison:
   - Flat: 18% risk, $1,240 avg
   - Kelly: 34% risk, $1,420 avg, higher variance
7. Educational insight: "Kelly grows faster but has higher risk of ruin"
```

### Workflow 6: Onboarding Tutorial (Dark Mode First Run)

```
1. User launches Betsim for the first time
2. App detects no settings/preferences saved
3. Onboarding modal appears:
   "Welcome to Betsim — the Monte Carlo betting simulator.
    In this 2-minute walkthrough, you'll learn how variance
    destroys bad bankroll strategies."
4. Step 1: Explain the inputs (odds, probability, bankroll)
   - "The key insight: your edge is your edge"
5. Step 2: User inputs -110 odds, 55% win probability, $1,000 bankroll
6. Step 3: Click "Run Simulation" → shows results instantly
   - "You won 62% of runs, but went broke 18% of the time"
7. Step 4: Educational insight
   - "Even with a 55% edge, you need proper bankroll management"
   - "Kelly Criterion suggests betting 4.5% of your bankroll per bet"
8. On completion: "Try it yourself" → workspace with example pre-filled
```

### Workflow 7: Scenario Library

```
1. User opens Simulation Workspace
2. Instead of entering params, clicks "Load Scenario"
3. Dropdown appears:
   - "NFL Favorite -3 @ -110" (pre-filled: odds -110, prob 65%, bankroll $1000, bet $50)
   - "MMA Underdog +200" (pre-filled: odds +200, prob 35%, bankroll $500, bet $25)
   - "3-Team NFL Parlay" (pre-filled: parlay odds 6.5, prob 15%, bankroll $500, bet $50)
   - "High-edge Value Play" (pre-filled: odds +150, prob 50%, bankroll $1000, bet $100)
4. User selects "NFL Favorite -3" → form auto-fills
5. User clicks "Run Simulation" → sees results immediately
6. Educational insight: "This strategy has positive EV but 22% risk of ruin"
```

### Workflow 8: Simulation History Browse

```
1. User navigates to Results History page
2. Sees a table: Date | Strategy | Params | Win % | Risk of Ruin | EV | Actions
3. Filters: by date range, sport, strategy name, or minimum win %
4. Clicks a row → expands to show charts + metrics from that run
5. Clicks "Re-run" → returns to workspace with same params
6. Clicks "Export CSV" → downloads that simulation's results
7. Clicking "Delete" removes from history (with confirmation)
```

---

## 5. Screen Designs

### 5.1 Simulation Workspace

```
┌─────────────────────────────────────────────────────────────────┐
│  Simulation Workspace                    [💾 Save] [📊 Export] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  BET PARAMETERS              │  SIMULATION RESULTS             │
│  ───────────────             │  ──────────────────             │
│                                                                 │
│  [Odds: -110]  → 52.38%     │  ┌──────┐ ┌──────┐ ┌──────┐    │
│  [Win prob: 55%]             │  │ Win% │ │Avg $ │ │Risk  │    │
│  [Bankroll: $1,000]          │  │ 62%  │ │1240  │ │18%   │    │
│  [Bet size: $50] [Flat ▼]    │  └──────┘ └──────┘ └──────┘    │
│  [Bets: 100]                 │  EV per bet: $2.27              │
│  [Simulations: 5,000]        │  Max drawdown: -45%             │
│                               │                                 │
│  [ RUN SIMULATION ]          │  Bankroll Trajectory        │
│                              │  [Chart: median + bands]    │
│                              │                                 │
│                              │  Distribution                │
│                              │  [Histogram]                  │
│                              │                                 │
│                              │  [ Save Strategy ]            │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 System Plays

```
┌─────────────────────────────────────────────────────────────────┐
│  System Plays Engine                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  MODEL INPUT              │  CALIBRATION REPORT               │
│  ─────────────            │  ──────────────────               │
│                                                                 │
│  [Odds: -110]             │  Stated probability:  60.0%        │
│  [Model prob: 60%]        │  Actual win rate:     59.9%        │
│  [Bankroll: $1,000]       │  Calibration error:   0.1%         │
│  [Bet size: 2% of bank]   │  Status:  🎯 Well Calibrated      │
│  [Bets: 100]              │  95% CI: [57.0%, 63.0%]           │
│  [Sims: 10,000]           │                                     │
│                           │  Recommendation:                    │
│  [ CALIBRATE MODEL ]       │  "Your model is accurate."        │
│                            │                                     │
│                            │  Probability Comparison:          │
│                            │  [Bar chart: stated vs. actual]   │
│                            │                                     │
│                            │  Simulation Results:              │
│                            │  [Same charts as Workspace]       │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Parlay Simulator

```
┌─────────────────────────────────────────────────────────────────┐
│  Parlay Simulator                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PARLAY BUILDER            │  PARLAY ANALYTICS                 │
│  ───────────────          │  ──────────────────               │
│                                                                 │
│  Selection 1:             │  Combined probability:  12.1%      │
│  [Odds: -110]             │  Combined payout:       9.07x       │
│  [Win prob: 55%]          │  EV:                    -26%         │
│  [✕ Remove]               │  Break-even need:       67% / leg   │
│                                                                 │
│  Selection 2:             │  Simulation Results:               │
│  [Odds: -110]             │  Win rate (actual):    ~12%        │
│  [Win prob: 55%]          │  Risk of ruin:         95%+        │
│  [✕ Remove]               │  Worst case:           -$1,000     │
│                                                                 │
│  Selection 3:             │  [ Distribution Chart ]            │
│  [Odds: +150]             │                                     │
│  [Win prob: 40%]          │  Insight: "Parlays require huge edge"│
│  [✕ Remove]               │                                     │
│                                                                 │
│  [+] Add Selection         │                                     │
│                           │                                     │
│  Bankroll: [$1,000]       │  [ Run Parlay Simulation ]        │
│  Bet size: [$100]          │                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Strategies Page

```
┌─────────────────────────────────────────────────────────────────┐
│  Strategies                       [ + New Strategy ]           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐                    │
│  │ NFL Week 1 (-5)  │  │ Parlay Test      │                    │
│  │ Odds: -110       │  │ Odds: 9.0x       │                    │
│  │ Prob: 55%        │  │ Prob: 12%        │                    │
│  │ Bankroll: $1,000 │  │ Bankroll: $1,000 │                    │
│  │ [Run] [Edit]     │  │ [Run] [Edit]     │                    │
│  └──────────────────┘  └──────────────────┘                    │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ Kelly 1/2 -6.5   │                                          │
│  │ Odds: -125       │                                          │
│  │ Prob: 52%        │                                          │
│  │ Bankroll: $500   │                                          │
│  │ [Run] [Edit]     │                                          │
│  └──────────────────┘                                          │
│                                                                 │
│  [ Load more... ]                                               │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 Settings

```
┌─────────────────────────────────────────────────────────────────┐
│  Settings                                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Display                                                       │
│  Theme: [● Dark (default)] ○ Light (disabled)                    │
│  Chart animations: [Enabled]                                   │
│                                                                 │
│  Simulation Defaults                                           │
│  Default simulations: [5,000]                                  │
│  Default bankroll: [$1,000]                                    │
│  Default num bets: [100]                                       │
│                                                                 │
│  Data Sources                                                  │
│  TheOddsAPI key: [••••••••••] [Edit]                           │
│  Auto-fetch odds: [Every 30 minutes]                           │
│                                                                 │
│  Storage                                                       │
│  Database location: ~/Library/Application Support/betsim/      │
│  [Change Location]                                             │
│                                                                 │
│  [ Save Settings ] [ Reset to Defaults ]                        │
└─────────────────────────────────────────────────────────────────┘
```

### 5.6 Simulation History

```
┌─────────────────────────────────────────────────────────────────┐
│  Results History                  [ Filter: All Time ▼ ] [Clear]│
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Date       Strategy      Odds   Prob  Bets  Sim   Win%   │  │
│  │─────────────┼────────────┼─────┼─────┼─────┼─────┼─────┤  │
│  │ 2026-01-14  NFL Week 1   -110  55%   100   5K   62%    │  │
│  │ 2026-01-14  Parlay Test  6.5x  12%   1    10K  12%    │  │
│  │ 2026-01-13  MLB Underdog +150  40%   100   10K  38%    │  │
│  │ 2026-01-12  Kelly -6.5   -125  52%   100   5K   55%    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  [ Re-run ] [ Export CSV ] [ View Charts ]                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Component Library

### Design Tokens

Dark mode only (optimized for nighttime use).

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | `#60A5FA` (Blue 400) | Buttons, links, active elements |
| `primary-hover` | `#93C5FD` (Blue 300) | Button hover |
| `secondary` | `#A78BFA` (Violet 400) | Secondary actions, accents |
| `success` | `#34D399` (Emerald 400) | Profit, good results |
| `warning` | `#FBBF24` (Amber 400) | Caution, moderate risk |
| `danger` | `#F87171` (Red 400) | Loss, high risk |
| `bg-primary` | `#0F172A` (Gray 900) | App background |
| `bg-secondary` | `#1E293B` (Gray 800) | Cards, panels |
| `bg-tertiary` | `#334155` (Gray 700) | Input backgrounds, borders |
| `text-primary` | `#F8FAF5` (Gray 50) | Main text |
| `text-secondary` | `#CBD5E1` (Gray 300) | Secondary text, labels |
| `text-muted` | `#94A3B8` (Gray 500) | Muted, disabled |
| `border` | `#475569` (Gray 600) | Borders, dividers |

### Key Components

| Component | Description | Used On |
|-----------|-------------|---------|
| `SimulationForm` | Input form for odds, probability, bankroll, bet size | Workspace |
| `ResultsCards` | Metric cards (win%, avg bankroll, risk of ruin) | Workspace, System Plays |
| `BankrollChart` | Multi-line chart: median + percentiles | Workspace, System Plays |
| `DistributionChart` | Histogram of final bankrolls | Workspace, System Plays, Parlay |
| `MetricsTable` | Table with all metrics | Workspace, System Plays |
| `StrategySelector` | Flat/Percentage/Kelly/Half-Kelly toggle | Workspace, Parlay |
| `KellyCalculator` | Live Kelly fraction display | Workspace, Parlay |
| `ParlayBuilder` | Add/remove/edit selections list | Parlay Simulator |
| `StrategyCard` | Saved strategy summary card | Strategies page |
| `CalibrationChart` | Stated vs. actual probability bars | System Plays |
| `IntelligenceScore` | Score breakdown + stars + risk level | Recommendation Detail, Portfolio |
| `PortfolioItem` | Single bet in portfolio view | Portfolio |
| `PortfolioView` | Full portfolio layout with confidence bands | Portfolio |
| `ExplainabilityPanel` | Top factors for model prediction | Recommendation Detail |
| `SaveStrategyModal` | Modal form for naming + saving | Workspace |
| `ExportButton` | CSV export of results | Workspace, System Plays, Portfolio |
| `OnboardingModal` | First-run tutorial walkthrough | App root (first launch only) |
| `ScenarioLibrary` | Pre-built betting scenarios dropdown | Workspace |
| `ResultsHistoryTable` | Table of past simulations | Results History page |
| `SettingsForm` | Display, defaults, data sources, storage | Settings page |
| `StrategyComparisonChart` | Overlayed bankroll trajectories | Workspace (comparison mode) |

### Chart Types

| Chart | Library | Data | Interaction |
|-------|---------|------|-------------|
| Bankroll Trajectory | Recharts LineChart | Median, p10, p90, min, max paths | Hover: tooltip with exact value at bet N |
| Distribution Histogram | Recharts BarChart | Binned final bankrolls | Hover: count + range |
| Calibration Bar | Recharts BarChart | Stated vs. actual probability | Hover: exact percentages |

---

## 7. Design Principles

### 1. Numbers First, Charts Second

The most important output is the metrics (win %, EV, risk of ruin). Charts are secondary and support the numbers. Design metric cards prominently.

### 2. Education Over Recommendations

Every result should include an educational insight:
- Good results → "Your edge is strong, but watch for variance."
- Bad results → "This strategy has negative EV. Kelly fraction: 0%."
- High risk of ruin → "Even with 55% win rate, you go broke 38% of the time."

### 3. Transparency

Always show:
- How many simulations ran
- Whether results are deterministic (seed shown)
- Implied probability vs. stated probability
- Edge calculation (stated prob vs. implied prob)

### 4. Progressive Disclosure

Start with basic inputs (odds, probability, bankroll). Advanced options (strategy type, number of simulations, Kelly criteria) are shown but don't overwhelm.

### 5. No Dark Patterns

- Never claim the model "predicts" winners
- Never hide the house edge
- Always show full distribution (including losses)
- Label clearly: "Simulation result" not "Prediction"

---

## 8. MVP Feature Checklist

### Sprint 0–8: Core MVP
- [ ] Electron + FastAPI scaffold running
- [ ] Database schema initialized
- [ ] Monte Carlo simulation engine
- [ ] EV, Kelly & bankroll calculations
- [ ] Backend API with /api/simulate + /api/strategies CRUD
- [ ] Simulation workspace UI (input form + results)
- [ ] Bankroll trajectory chart
- [ ] Distribution histogram
- [ ] Strategies page (save/load/edit/delete)
- [ ] CSV export
- [ ] Risk of ruin calculator
- [ ] Three bankroll strategies (Flat, Percentage, Kelly)

### Sprint 9: Data Integration
- [ ] Live odds from TheOddsAPI
- [ ] Odds selector in workspace
- [ ] Feature schema defined

### Sprint 10: System Plays Engine
- [ ] Calibration engine (stated vs. actual probability)
- [ ] Calibration report + chart
- [ ] Educational insights

### Sprint 11: Parlay + Bankroll Comparison
- [ ] Parlay builder (2-6 selections)
- [ ] Strategy toggle (Flat/Percentage/Kelly)
- [ ] Side-by-side comparison

### Sprint 12: Backtesting Engine
- [ ] Historical replay against actual results
- [ ] Model evaluation (accuracy, ROI, calibration)
- [ ] Analytics dashboard

### Sprint 13: ML Pipeline & Explainability
- [ ] ProbabilityModel interface
- [ ] Feature extraction pipeline
- [ ] Training pipeline structure
- [ ] Explainability (top factors)

### Sprint 14: Intelligence Score & Portfolio
- [ ] Intelligence Score (92/100-style aggregate)
- [ ] Portfolio Construction (confidence bands)
- [ ] Full test suite (backend + frontend)
- [ ] Electron packaging

---

## 9. Intelligence Score

### Concept

Every recommendation gets an **Intelligence Score** (0–100) — an aggregate rating that combines probability, simulation results, EV, model confidence, and calibration. This is SIP's unique differentiator instead of simply saying "Bet this."

### Score Breakdown

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

### Screen Design: Recommendation Detail

```
┌─────────────────────────────────────────────────────────┐
│  Boston Bruins ML vs. Toronto Maple Leafs        [92/100]│
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────────────────────────────┐      │
│  │  Intelligence Score: 92/100   ★★★★☆          │      │
│  └──────────────────────────────────────────────┘      │
│                                                         │
│  Score Breakdown:                                       │
│  ├─ Probability (25%)     74% → 18.5 points              │
│  ├─ Simulation (25%)     81% → 20.3 points              │
│  ├─ Expected Value (25%)  +8.3% → 20.8 points            │
│  ├─ Model Confidence (15%) 88% → 13.2 points            │
│  ├─ Calibration (10%)   Good → 10.0 points              │
│  └───────────────────────────────────────────────────────┤
│  Total: 82.8/100 → Rounded to 92/100 (with bonus)      │
│                                                         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐          │
│  │Prob  │ │Sim   │ │EV    │ │Confid│ │Calib │          │
│  │74%   │ │81%   │ │+8.3% │ │88%   │ │Good  │          │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘          │
│                                                         │
│  Top Factors:                                           │
│  + Home Advantage (+12% effect on probability)          │
│  + Opponent Back-to-back (-8% opponent fatigue)          │
│  + Better Offensive Rating (+7% scoring edge)           │
│  + Better Net Rating (+9% overall performance)            │
│                                                         │
│  [ 🔍 Simulate This Bet ] [ 💾 Add to Portfolio ]       │
└─────────────────────────────────────────────────────────┘
```

### Score Calculation

```python
def calculate_intelligence_score(
    predicted_prob: float,
    simulation_win_rate: float,
    ev: float,
    model_confidence: float,
    calibration_status: str,
) -> dict:
    """
    Weights: Probability 25%, Simulation 25%, EV 25%, Confidence 15%, Calibration 10%
    """
    probability_points = (predicted_prob / 1.0) * 25  # normalized 0-1
    simulation_points = (simulation_win_rate / 1.0) * 25
    ev_points = sigmoid(ev / 0.10) * 25  # +10% EV → ~22 points, -10% → ~3 points
    confidence_points = model_confidence * 15
    calibration_points = 10 if calibration_status == "well_calibrated" else 5

    raw_score = probability_points + simulation_points + ev_points + confidence_points + calibration_points
    # Bonus multipliers:
    if ev > 0.10: raw_score += 5  # strong positive EV bonus
    if calibration_status == "well_calibrated": raw_score += 3
    if simulation_win_rate > predicted_prob: raw_score += 2  # simulation agrees

    return {
        "score": round(min(raw_score, 100)),
        "breakdown": {
            "probability": {"value": predicted_prob, "points": round(probability_points, 1), "max": 25},
            "simulation": {"value": simulation_win_rate, "points": round(simulation_points, 1), "max": 25},
            "ev": {"value": ev, "points": round(ev_points, 1), "max": 25},
            "confidence": {"value": model_confidence, "points": round(confidence_points, 1), "max": 15},
            "calibration": {"value": calibration_status, "points": round(calibration_points, 1), "max": 10},
        },
        "stars": 5 if raw_score >= 85 else (4 if raw_score >= 70 else (3 if raw_score >= 55 else (2 if raw_score >= 40 else 1))),
        "risk_level": "Low" if ev < 0.10 else ("Medium" if ev < 0.20 else "High"),
    }
```

### Risk Levels

| Score | Stars | Risk | Description |
|-------|-------|------|-------------|
| 85–100 | ★★★★★ | Low | Strong play, highly recommended |
| 70–84 | ★★★★☆ | Low–Medium | Solid play, worth considering |
| 55–69 | ★★★☆☆ | Medium | Speculative, moderate risk |
| 40–54 | ★★☆☆☆ | High | Avoid unless high-risk tolerance |
| 0–39 | ☆☆☆☆☆ | Extreme | Do not bet |

---

## 10. Portfolio Construction

### Concept

Instead of recommending isolated bets, the engine constructs a **daily portfolio** of bets with risk allocation across confidence levels. This is portfolio theory applied to sports betting.

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

### Screen Design: Portfolio

```
┌─────────────────────────────────────────────────────────┐
│  Today's Portfolio — 2026-01-15             [📊 Export] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Summary:                                               │
│  ┌──────┬─────────┬────────────────┬──────────┐        │
│  │Level │ Bets    │ Allocation     │ ROI      │        │
│  ├──────┼─────────┼────────────────┼──────────┤        │
│  │High  │ 2       │ 40%            │ 12.0%    │        │
│  │Med   │ 4       │ 30%            │ 8.0%     │        │
│  │Low   │ 6       │ 20%            │ 4.0%     │        │
│  └──────┴─────────┴────────────────┴──────────┘        │
│                                                         │
│  Key Metrics:                                           │
│  Total Risk:     6%                                     │
│  Expected ROI:   8.0%                                    │
│  Kelly Exposure: 12%                                     │
│  Max Drawdown:   -15% (from simulations)                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ High Confidence Picks                           │    │
│  │                                                 │    │
│  │ 1. Boston ML ★★★★☆  Score: 92  Stake: $200     │    │
│  │    Prob: 74%  EV: +8.3%  Sim: 81%              │    │
│  │                                                 │    │
│  │ 2. Dallas ML ★★★★☆  Score: 88  Stake: $150     │    │
│  │    Prob: 68%  EV: +7.1%  Sim: 73%              │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │ Medium Confidence Picks                         │    │
│  │                                                 │    │
│  │ 3. Miami ML ★★★☆☆   Score: 78  Stake: $75     │    │
│  │ 4. Denver ML ★★★☆☆   Score: 72  Stake: $50     │    │
│  │ 5. Chicago ML ★★★☆☆  Score: 76  Stake: $60     │    │
│  │ 6. Portland ML ★★★☆☆ Score: 74  Stake: $45     │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  [ 🔄 Rebalance Portfolio ] [ 📤 Export Picks ]       │
└─────────────────────────────────────────────────────────┘
```

---

## Feature Spec: Key Screens

### Simulation Workspace — Input Form

```
FIELD          | TYPE         | VALIDATION         | HELPER TEXT
--------------|--------------|--------------------|------------------
Odds (American)| number       | Required, +/- range| Implied prob: XX%
Win Probability| percentage   | 0%–100%            | Your edge estimate
Bankroll       | currency     | > $0               | Starting bankroll
Bet Size       | number/%     | > $0 (or 1%–100%)  | Per bet stake
Bet Strategy   | radio select | flat/percentage/   | Kelly auto-calculates
              |              | kelly/half_kelly   | fraction from odds+prob
Num Bets       | number       | 1–10,000           | Per simulation run
Num Simulations| number       | 1,000–100,000      | More = slower, more accurate
[ RUN SIMULATION ]                  | Loading state | Error handling
```

### Risk of Ruin Logic

> "You will go broke X% of the time"

Risk of ruin is calculated as: **percentage of simulations where bankroll reaches $0**.

- If bankroll drops to $0 at any point during the bet sequence → that run is "broke"
- Risk of Ruin = (number of broke runs) / (total simulations)

**Warning thresholds:**
- < 10% → Low risk (green)
- 10–25% → Moderate risk (amber)
- > 25% → High risk (red) — show warning: "This strategy is aggressive"

### Edge Calculation

> "Your strategy only profits long term if edge > X%"

Edge = (Stated Win Probability × Decimal Odds) - 1

Example:
- Odds: -110 (decimal 1.909)
- Stated probability: 55%
- Edge = (0.55 × 1.909) - 1 = 1.05 - 1 = 0.05 → 5% edge

If edge > 0 → positive EV, long-term profitability
If edge ≤ 0 → negative EV, long-term losses

This is shown as: "Your edge: +5.0% (positive)" or "Your edge: -2.8% (negative)"

---

*This document defines WHAT we build and HOW it looks. It is intentionally lightweight on visual design specifics (colors, spacing) and heavy on user workflows, feature specs, and decision frameworks. Visual polish is deferred to implementation time.*
