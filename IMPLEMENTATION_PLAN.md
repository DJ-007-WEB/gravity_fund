# Gravity Fund — Implementation Plan
### Quantitative Retail Wealth Optimization Platform (Indian Markets — NSE/BSE)

---

## What We're Building

A platform that helps Indian retail investors make disciplined, risk-aware portfolio decisions
instead of emotional, speculative trades. It provides personalized asset allocation, risk
analytics, and behavioral guardrails — backed by real quantitative finance math, not black-box AI.

---

## Tech Stack

| Layer          | Choice                              |
|----------------|--------------------------------------|
| Frontend       | Next.js (TypeScript)                |
| Backend        | FastAPI (Python, async)             |
| Database       | PostgreSQL                          |
| Cache          | Redis (single instance)            |
| Quant Engine   | NumPy, Pandas, SciPy, PyPortfolioOpt|
| Market Data    | yfinance (NSE: `.NS`, BSE: `.BO`)  |
| Scheduler      | APScheduler (in-process)           |
| Auth           | JWT (python-jose + passlib)        |

---

## Architecture (Phase 1 — Monolith)

Everything runs as a single FastAPI process. No microservices, no message brokers,
no Docker required for local development.

```
Next.js Client
    │
    │  HTTPS / WSS
    ▼
┌──────────────────────────────────────────┐
│         FastAPI Monolith                 │
│                                          │
│  ┌─────────────────────────────────┐     │
│  │  Gateway & Router               │     │
│  │  (Auth middleware, JWT, rate     │     │
│  │   limiting)                     │     │
│  └──────────┬──────────────────────┘     │
│             │                            │
│  ┌──────────┼──────────┬────────────┐    │
│  │          │          │            │    │
│  ▼          ▼          ▼            │    │
│ User      Quant      Data          │    │
│ Profiling Engine     Ingestion     │    │
│            │        (APScheduler)   │    │
│            │          │            │    │
│            ▼          │            │    │
│   BackgroundTasks     │            │    │
│                       ▼            │    │
│               Market Data API      │    │
│               (NSE / Yahoo)        │    │
└──────────┬───────────────────┬─────┘    │
           │                   │
           ▼                   ▼
     PostgreSQL             Redis
  (users, portfolios,    (sessions, calc
   price history)        results, market
                         data cache)
```

---

## Project Structure

```
gravity_fund/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point + lifespan
│   │   ├── core/                # Config, security, redis client
│   │   ├── db/
│   │   │   ├── models/          # SQLAlchemy ORM models
│   │   │   ├── session.py       # DB connection setup
│   │   │   └── base.py          # Declarative base
│   │   ├── schemas/             # Pydantic request/response models
│   │   ├── api/
│   │   │   ├── middleware/      # JWT auth, rate limiting
│   │   │   ├── v1/              # Versioned route handlers
│   │   │   └── deps.py          # Dependency injection
│   │   ├── services/            # Business logic layer
│   │   ├── engines/             # Quant math (MPT, risk, Monte Carlo)
│   │   └── jobs/                # APScheduler + data ingestion
│   ├── alembic/                 # DB migrations
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
└── frontend/                    # Next.js app
```

---

## Database Models

### users
- id, email, password_hash, is_active, created_at

### user_profiles
- user_id, age, annual_income, monthly_expenses, investment_horizon_years,
  risk_tolerance_answers (JSONB), risk_score, risk_category

### assets
- ticker (e.g. NIFTYBEES.NS), name, asset_class (equity/bond/commodity/cash)

### historical_prices
- asset_id, date, open, high, low, close, adj_close, volume
- Unique constraint on (asset_id, date)

### portfolios
- user_id, name, status (pending/optimized/failed),
  optimization_params (JSONB), result_weights (JSONB), risk_metrics (JSONB)

---

## API Endpoints

### Auth
- `POST /api/v1/signup` — Register
- `POST /api/v1/login` — Get JWT token
- `POST /api/v1/logout` — Invalidate token

### Profile
- `GET /api/v1/profile` — Get current user profile
- `PUT /api/v1/profile` — Update profile
- `POST /api/v1/profile/risk-assessment` — Submit risk questionnaire, get score

### Portfolio
- `POST /api/v1/portfolios/optimize` — Request optimization (returns 202 + task_id)
- `GET /api/v1/portfolios/{id}` — Get portfolio result
- `GET /api/v1/portfolios` — List user portfolios

### Market
- `GET /api/v1/market/assets` — List supported assets
- `GET /api/v1/market/prices/{ticker}` — Get price history

---

## Quant Engine — What It Calculates

The `engines/` folder contains pure math functions. No database, no FastAPI imports.
It takes in raw numpy arrays or pandas DataFrames and returns results.

### Portfolio Optimization (optimizer.py)
- Mean-Variance Optimization (Markowitz / MPT)
- Uses PyPortfolioOpt to compute optimal asset weights
- Input: historical returns DataFrame + constraints
- Output: dict of {ticker: weight} summing to 1.0

### Risk Metrics (risk.py)
- Sharpe Ratio
- Sortino Ratio
- Maximum Drawdown
- Value at Risk (VaR) — parametric and historical
- Conditional VaR (CVaR / Expected Shortfall)
- Beta (vs Nifty 50 benchmark)

### Monte Carlo Simulation (simulator.py)
- Simulates N portfolio paths over a given horizon
- Returns percentile bands (5th, 25th, 50th, 75th, 95th)
- Used to show users probability ranges of outcomes

---

## Default Asset Universe (Indian Markets)

| Ticker            | Name                        | Class     |
|-------------------|-----------------------------|-----------|
| NIFTYBEES.NS      | Nippon Nifty 50 ETF         | Equity    |
| JUNIORBEES.NS     | Nippon Nifty Next 50 ETF    | Equity    |
| BANKBEES.NS       | Nippon Bank Nifty ETF       | Equity    |
| GOLDBEES.NS       | Nippon Gold ETF             | Commodity |
| LIQUIDBEES.NS     | Nippon Liquid ETF           | Cash      |
| CPSEETF.NS        | CPSE ETF                    | Equity    |
| SETFNIF50.NS      | SBI Nifty 50 ETF            | Equity    |
| ICICILIQ.NS       | ICICI Liquid ETF            | Cash      |

Tickers use the `.NS` suffix for NSE (via yfinance).

---

## How Async Works (No Celery Needed in Phase 1)

Heavy computations (optimization, Monte Carlo) run via FastAPI BackgroundTasks:

1. User hits `POST /portfolios/optimize`
2. API creates a portfolio record with `status = "pending"`
3. API schedules the math via `BackgroundTasks`
4. API immediately returns `202 Accepted` with the portfolio ID
5. Background thread runs the optimizer, writes results to DB + Redis cache
6. User polls `GET /portfolios/{id}` until `status = "optimized"`

For tasks that could block the GIL (heavy NumPy loops), use `ProcessPoolExecutor`.

---

## Redis Key Namespaces

Single Redis instance, separated by key prefixes:

| Purpose           | Key Pattern                    | TTL        |
|--------------------|--------------------------------|------------|
| User sessions      | `session:{user_id}`           | 24 hours   |
| Rate limiting      | `ratelimit:{ip}`              | 60 seconds |
| Calc results cache | `calc:{portfolio_id}:{hash}`  | 7 days     |
| Market data cache  | `market:{ticker}:latest`      | Until next EOD refresh |

---

## Risk Scoring Algorithm (User Profiling)

Users answer a questionnaire (5–10 questions) about:
- Investment horizon
- Reaction to market drops
- Income stability
- Financial dependents
- Prior investment experience

Each answer maps to a score (1–5). Total score maps to a category:

| Score Range | Category      | Suggested Equity Allocation |
|-------------|---------------|------------------------------|
| 5–10        | Conservative  | 20–30%                       |
| 11–18       | Moderate      | 40–60%                       |
| 19–25       | Aggressive    | 70–90%                       |

---

## Build Order

1. **Core setup** — config, DB connection, Redis client
2. **Models + migrations** — all SQLAlchemy models, Alembic
3. **Auth** — signup, login, JWT middleware, rate limiter
4. **Profiling** — risk questionnaire, scoring
5. **Quant engine** — optimizer, risk metrics, simulator (pure math, tested standalone)
6. **Portfolio API** — wire engine to API via BackgroundTasks
7. **Data ingestion** — APScheduler + yfinance fetcher
8. **Market API** — expose price data endpoints
9. **Tests** — unit tests for engine, integration tests for API
10. **Frontend** — Next.js pages, functional first, polish later

---

## What Phase 2 Adds (Future)

- Celery + RabbitMQ replacing BackgroundTasks
- Separate Redis instances (session vs cache)
- PgBouncer for connection pooling
- WebSocket push for real-time optimization status
- Behavioral warning system (overtrading detection, concentration alerts)
- Docker + CI/CD pipeline
