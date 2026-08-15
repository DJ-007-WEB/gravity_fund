# Gravity Fund MVP data plan

## Product boundary before data collection

Until Gravity Fund operates under the appropriate SEBI registration or a formal
partnership with a registered adviser, the application must remain an educational
analytics and portfolio-planning tool. Do not present a personalised security-level
buy, sell, or hold instruction, promise a return, or connect automated execution.

## Acquire now: narrow, reproducible daily data

The first optimisation MVP only needs end-of-day data for a small, liquid universe:

| Dataset | MVP use | Initial source | Store |
| --- | --- | --- | --- |
| Instrument master | Ticker, name, asset class, benchmark, start/end date | Manually curated and reviewed from NSE/BSE issuer pages | `assets` |
| Daily OHLCV and adjusted close | Returns, drawdown, volatility, backtests | Development: yfinance for the approved NSE tickers. Production: a licensed exchange/vendor feed. | `historical_prices` |
| Nifty 50 benchmark history | Beta and performance comparison | NSE index data or a licensed vendor | `historical_prices` with a benchmark asset |
| Cash/debt reference series | Conservative allocation and scenario assumptions | RBI T-bill / government-securities publications | dedicated macro/rates table in the next migration |
| Asset metadata | Expense ratio, underlying index, issuer, liquidity review date | ETF issuer factsheets and exchange disclosures | `assets` metadata in the next migration |

Start with the eight ETFs already listed in `IMPLEMENTATION_PLAN.md`, plus one
benchmark. Download at least five years of daily observations where available. Keep
the raw payload, source URL, retrieval timestamp, timezone, adjustment method, and
ingestion version for every batch; never overwrite the raw source silently.

## Do not acquire yet

- Real-time ticks or an expensive market-data subscription: required only for live
  alerts or execution, not a daily portfolio-planning MVP.
- Broker credentials, holdings, transaction history, or tax lots: acquire only after
  explicit user consent, a provider agreement, encryption/key-management design,
  retention policy, and a concrete portfolio-import feature.
- ML training data: do not train on a tiny or unlabelled investment dataset. Begin
  with deterministic, explainable portfolio rules. Revisit ML only after consented,
  governed product-event data exists and a measurable decision problem is defined.
- Social/news sentiment feeds: not needed for long-horizon allocation and likely to
  introduce noise and explainability risk.

## When to add each dataset

1. **Now, before the quant engine:** curated ETF universe, daily price history,
   benchmark, and basic rates. Validate missing dates, duplicate dates, corporate
   action adjustments, and outliers on every ingestion run.
2. **After profile + allocation MVP:** issuer metadata, expense ratios, tracking
   differences, and liquidity safeguards. These make the recommendation explainable.
3. **After an explicit consent flow:** read-only portfolio imports and tax-lot data.
   Encrypt data at rest, record consent/version, minimise retention, and provide
   deletion/export workflows.
4. **Only after a regulated advice/execution decision:** licensed real-time data,
   broker integrations, and trade/audit records.

## Data quality gates

Every ingestion job must reject or quarantine rows with an unknown ticker, duplicate
asset/date pair, negative price, impossible OHLC relation, invalid volume, stale
timestamp, or missing source metadata. Calculations must display their as-of date and
must not run when a required asset series is stale or below its minimum history.
