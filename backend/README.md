# Gravity Fund backend

## Run locally

1. Copy `.env.example` to `.env` inside this directory and replace `JWT_SECRET_KEY`
   with a long, random value. Never commit this file.
2. Start PostgreSQL and Redis with `docker compose up -d` from the repository root.
3. Install dependencies and run `alembic upgrade head` from this directory.
4. Start the API with `uvicorn app.main:app --reload`.

The public liveness check is `GET /api/v1/health`. `GET /api/v1/ready` checks both
PostgreSQL and Redis and should be used by deployment infrastructure.

## Current API boundary

- `/auth/*`: account and session endpoints
- `/profile`: authenticated profile and transparent risk assessment
- `/health`, `/ready`: operational endpoints

The current risk score is a deterministic suitability input, not an investment
recommendation. Portfolio construction is intentionally not exposed until its data,
constraints, validation, and regulatory boundary are implemented.
