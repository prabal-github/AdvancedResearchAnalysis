# Portfolio Insurance Module Documentation

File: `portfolio_insurance.py`
Status: Prototype scaffold (educational). NOT production‑ready.

---
## 1. Purpose
Provide a framework for offering a time‑bounded downside protection ("insurance") on an equity / ETF portfolio using listed index options (protective put or cost‑reduced collar). The system produces a policy *draft* that can later be bound (executed) by placing option orders via a broker API (e.g. Upstox) and tracked until expiry.

---
## 2. Core Concepts
| Concept | Description |
|---------|-------------|
| Policy | A hedge contract covering a portfolio for a defined term with a floor (e.g. 90% of initial value). |
| Floor % | Minimum protected value as a percent of initial portfolio value (e.g. 0.90). |
| Strategy | `protective_put` (buy puts) or `collar` (buy put + sell OTM call). |
| Coverage Notional | Amount of exposure hedged (can be full portfolio * beta or partial). |
| Beta | Relative sensitivity of portfolio vs chosen index (simplified averaging here). |
| Hedge Legs | Option positions (put leg required; call leg optional). |
| Premium Net | Estimated net cost (put premium minus call premium if collar). |
| Settlement | Evaluation of hedge intrinsic value vs actual shortfall below floor. |

---
## 3. Data Structures (Dataclasses)
- `Position(symbol, quantity, asset_type, beta)`
- `OptionQuote(symbol, expiry, strike, option_type, last_price, bid, ask, underlying)`
- `HedgeLeg(option, contracts, side, est_cost)`
- `PolicyDraft(portfolio_value, beta, coverage_notional, floor_pct, start_utc, end_utc, strategy, index_symbol, put_leg, call_leg, premium_net, metadata)`

These are **in-memory only** in the current scaffold.

---
## 4. Workflow Overview
1. Gather current portfolio positions & prices.
2. Estimate beta vs chosen index (placeholder: average of provided betas, default 1.0).
3. Compute portfolio value.
4. Fetch index level (`yfinance` fallback) and synthetic option chain (placeholder) OR real chain via broker.
5. Select strikes:
   - Put strike ≈ index * floor% (rounded to nearest 50).
   - Call strike (collar) ≈ index * (1 + upside_cap_pct).
6. Size contracts: `ceil(coverage_notional / (index_level * contract_multiplier))`.
7. Build `PolicyDraft` with cost estimates.
8. Present draft to user for acceptance.
9. (Future) On acceptance: place orders, store persistent policy row, start monitoring jobs.
10. Settlement: compute intrinsic payoff and compensation vs floor.

---
## 5. Key Functions
| Function | Purpose |
|----------|---------|
| `estimate_portfolio_beta` | Placeholder beta estimator (average provided betas). |
| `compute_portfolio_value` | Sums quantity * price. |
| `required_put_notional` | Determines hedge notional (currently full value; can refine). |
| `select_put_strike` / `select_call_strike` | Strike rounding logic. |
| `contracts_needed` | Option contract sizing. |
| `fetch_index_level` | Uses `yfinance` (fallback static). |
| `fetch_option_chain` | Placeholder synthetic chain generator. Replace with real broker API. |
| `build_policy_draft` | Orchestrates full draft creation. |
| `estimate_policy_payoff` | Computes indicative settlement metrics. |

---
## 6. Example Usage (from module `__main__`)
```python
sample_positions = [
    Position(symbol='AAPL', quantity=10, beta=1.1),
    Position(symbol='MSFT', quantity=8, beta=1.0),
    Position(symbol='SPY', quantity=5, beta=1.0),
]
prices = {'AAPL': 210, 'MSFT': 430, 'SPY': 560}

draft = build_policy_draft(
    positions=sample_positions,
    price_map=prices,
    floor_pct=0.90,
    term_days=30,
    strategy='collar'
)
print(draft)

payoff = estimate_policy_payoff(
    draft,
    final_portfolio_value=draft.portfolio_value * 0.88,
    final_index_level=fetch_index_level(draft.index_symbol) * 0.9
)
print(payoff)
```

---
## 7. Implementation Roadmap (Integration Steps)
### Phase 1: Persistence & API (Read / Draft)
- Create DB model `InsurancePolicy` (see suggested schema in code header comment).
- Endpoint: `POST /api/insurance/quote` – body: positions snapshot, floor_pct, term_days, strategy.
- Use `build_policy_draft`; return draft JSON.

### Phase 2: Bind (Order Placement)
- Endpoint: `POST /api/insurance/bind` – accepts draft id or full draft payload + user confirmation.
- Call broker (Upstox) to place option orders:
  - Validate liquidity (bid/ask) and slippage tolerance.
  - Store transaction IDs.
- Persist:
  - status = `active`
  - record premiums (actual executed prices not estimates).

### Phase 3: Monitoring
- Scheduled job (Celery / APScheduler): every N minutes / EOD
  - Revalue portfolio (fetch current prices).
  - Check floor breach / near-breach alert.
  - Update MTM of hedge (using mid or last). 
  - Write snapshots to `insurance_policy_nav` table.

### Phase 4: Early Trigger Handling (Optional)
- If user selected early-trigger payout (e.g. catastrophic drop), allow claim evaluation before expiry.
- Endpoint: `POST /api/insurance/claim` verifying conditions.

### Phase 5: Settlement
- On expiry:
  - Compute intrinsic value of put (or collar net).
  - Compute shortfall below floor.
  - Compensation = min(shortfall, hedge payoff) (adjust per legal terms).
  - Create ledger entry / credit investor wallet.
  - Update policy status = `settled`.

### Phase 6: Risk & Pricing Enhancements
- Replace placeholder pricing with implied vol surfaces; compute theoretical premium.
- Support partial coverage (hedge (1 - floor_pct) share only) for lower cost.
- Add dynamic delta hedging alternative strategies.

### Phase 7: Analytics & UI
- Dashboard: Active policies, coverage %, time to expiry, MTM P/L.
- Historical performance: show portfolio vs insured floor vs payout.

---
## 8. Suggested Database Schema (Illustrative)
```sql
CREATE TABLE insurance_policies (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  status TEXT NOT NULL,                 -- draft|active|expired|settled|cancelled
  created_at DATETIME NOT NULL,
  start_utc DATETIME NOT NULL,
  end_utc DATETIME NOT NULL,
  floor_pct REAL NOT NULL,
  index_symbol TEXT NOT NULL,
  strategy TEXT NOT NULL,
  put_strike REAL NOT NULL,
  call_strike REAL,
  contracts_put INTEGER NOT NULL,
  contracts_call INTEGER,
  premium_put REAL NOT NULL,
  premium_call REAL,
  premium_net REAL NOT NULL,
  coverage_notional REAL NOT NULL,
  portfolio_value_at_bind REAL NOT NULL,
  beta REAL NOT NULL,
  breach_flag INTEGER DEFAULT 0,
  notes TEXT
);
```
Additional tables:
- `insurance_policy_nav(policy_id, ts, portfolio_value, index_level, hedge_value, shortfall, intrinsic_est)`
- `insurance_policy_events(policy_id, ts, event_type, details_json)`

---
## 9. API Contract Sketch
### POST /api/insurance/quote
Request:
```json
{
  "positions": [{"symbol": "AAPL", "quantity": 10, "beta": 1.1}],
  "prices": {"AAPL": 210},
  "floor_pct": 0.9,
  "term_days": 30,
  "strategy": "protective_put"
}
```
Response:
```json
{
  "ok": true,
  "draft": {"portfolio_value": 123456.7, "put_leg": {"strike": 18000, "contracts": 12, ...}, "premium_net": 2450.0}
}
```

### POST /api/insurance/bind
- Validates draft, executes orders, persists policy.

### GET /api/insurance/policies/{id}
- Returns current MTM, shortfall, remaining days.

### POST /api/insurance/settle (internal/cron)
- Settles matured policies.

---
## 10. Hedging Logic Notes
- **Contract Multiplier**: Hardcoded (e.g. 50). Must align with actual index derivative spec.
- **Slippage / Liquidity**: In production require bid/ask snapshot and allowable slippage checks.
- **Risk Concentration**: Limit maximum insured notional per index & per user.

---
## 11. Payoff Mechanics (Simplified)
```
Floor Value = floor_pct * initial_portfolio_value
Shortfall = max(0, Floor Value - final_portfolio_value)
Put Intrinsic = max(0, Put Strike - Final Index Level) * multiplier * contracts
Compensation = min(Shortfall, Put Intrinsic)
```
Enhancements:
- Collar: subtract short call intrinsic (if ITM) from put payoff.
- Partial Coverage: scale by coverage_ratio.

---
## 12. Validation & Edge Cases
| Case | Handling (current) | Future Improvement |
|------|--------------------|--------------------|
| Missing price | Skip position | Fallback price source / reject draft |
| No put at strike | Raise error | Pick nearest strike / interpolate |
| Zero beta | Hedge full notional | Compute robust multi-factor beta |
| Illiquid option | Not modeled | Liquidity filter + alt strike |
| Early termination | Not modeled | Add cancellation & unwind logic |

---
## 13. Extension Ideas
- Parametric crash triggers (e.g. > X% intraday drop auto-payout component).
- Dynamic rebalancing (roll hedge if delta drift > threshold).
- Multi-index hedge allocation (optimize variance reduction).
- Machine learning premium adjustment based on realized vol vs implied.
- Portfolio scenario simulator UI (before buying insurance).

---
## 14. Security / Compliance Considerations
- Regulatory classification (derivatives advice, insurance licensing vs structured product).
- KYC & suitability (limit advanced strategies to approved users).
- Logging of all strike / notional decisions (audit trail).
- Rate limiting on quote generation to prevent resource abuse.

---
## 15. Deployment & Operations
| Component | Frequency / Trigger | Tooling |
|-----------|---------------------|---------|
| Quote generation | On demand | Flask API |
| Policy bind | User confirmation | Broker API integration |
| Monitoring | Cron / scheduler (5–15m) | APScheduler / Celery |
| Settlement | Daily EOD + expiry checks | Scheduled job |
| Metrics | Continuous | Prometheus / logs |

---
## 16. Known Limitations
- Synthetic option chain (no real greeks / IV surface).
- No margin / capital usage modeling.
- Beta model trivial.
- No persistence or API wiring yet.
- No hedging order execution or error handling.

---
## 17. Next Action Checklist
- [ ] Add DB models.
- [ ] Implement `/api/insurance/quote` endpoint.
- [ ] Implement `/api/insurance/bind` with Upstox integration.
- [ ] Create monitoring job & NAV snapshot table.
- [ ] Implement settlement job & ledger credit.
- [ ] Build admin dashboard for active policies.
- [ ] Add unit tests (draft sizing, payoff calc, edge cases).
- [ ] Replace synthetic chain with real chain provider.
- [ ] Add comprehensive logging + alerts.

---
## 18. Quick Start (Local Draft Only)
```python
from portfolio_insurance import Position, build_policy_draft, estimate_policy_payoff, fetch_index_level

positions = [Position('AAPL', 10, beta=1.1), Position('MSFT', 5, beta=1.0)]
prices = {'AAPL': 210, 'MSFT': 430}

draft = build_policy_draft(positions, prices, floor_pct=0.9, term_days=30, strategy='protective_put')
print(draft)

payoff = estimate_policy_payoff(
    draft,
    final_portfolio_value=draft.portfolio_value * 0.85,
    final_index_level=fetch_index_level(draft.index_symbol)*0.9
)
print(payoff)
```

---
## 19. Support & Ownership
- Interim Owner: (Assign developer)  
- Escalation: Risk engineering lead  
- Documentation updates: Include version/date header.

Version: 0.1 (Scaffold)  
Last Updated: (auto) Initial creation

---
## 20. AI / ML / LLM Driven Uncertainty & Opportunity Engine

This extension layer continuously scans markets, macro calendars, news, and internal signals to:
1. Detect potential future uncertainty windows (e.g. high-vol earnings cluster, macro announcements, geo‑political escalation probability, volatility regime shifts).
2. Quantify forward risk distribution (expected drawdown bands, volatility expansion, correlation spikes).
3. Map each predicted uncertainty window to the optimal tradable option expiries & structures for hedge or strategic opportunity.
4. Express findings in natural language (LLM) as:  
  “Uncertainty expected (reason) between (start→end). Opportunity: (hedge / strategy) with estimated cost X, potential protection Y, residual risk Z.”
5. Provide interactive scenario testing: user tweaks severity; engine recomputes P/L + hedge payoff vs unhedged baseline.

### 20.1 Data & Signal Inputs
| Category | Sources | ML Tasks |
|----------|---------|---------|
| Macro & Events | Economic calendar (CPI, FOMC, Jobs), corporate earnings schedule | Time window risk tagging |
| Market Microstructure | Real‑time index & sector volatility, implied vol term structure, skew | Regime classification, volatility forecasting |
| News / NLP | News APIs, social sentiment, filings | Event clustering, sentiment scoring, entity risk tagging |
| Portfolio Internals | Position concentration, leverage, liquidity, beta drift | Stress amplification scoring |
| External Risk Feeds | Geo‑political risk indices, credit spreads | Tail risk probability adjustment |

### 20.2 Model Components
| Component | Role |
|----------|------|
| Vol Forecast (GARCH / LSTM / Prophet hybrid) | Predict short-term realized vol interval & confidence band |
| Jump / Anomaly Detector (Isolation Forest / EVT) | Flag abnormal return dispersion or volume spikes |
| Correlation Regime Switch (HMM) | Detect transition to high systemic correlation |
| Event Impact Classifier (Gradient Boost / Transformer) | Score expected absolute move given upcoming event |
| Tail Distribution Estimator (Monte Carlo + Cornish-Fisher) | Estimate 1–5 day expected shortfall & crash tail |
| LLM Narrative Generator | Summarize drivers, translate quantitative outputs into user-facing rationale & action items |
| Strategy Recommender (Rule + ML ranking) | Rank hedge structures by cost efficiency (Cost / Protection %) |

### 20.3 Expiry & Strike Recommendation Logic
1. Determine uncertainty window [T0, T1].
2. List nearest listed expiries >= T1; include one prior & one after for optional early exit / carry efficiency.
3. For each expiry candidate:
  - Compute projected portfolio variance over life.
  - Estimate hedge theta decay vs needed coverage horizon.
  - Score = (Expected Shortfall Reduction – Premium Cost) / Residual Risk.
4. Choose top structure per strategy family:
  - Protective Put: floor_pct = 1 – target_drawdown.
  - Collar: choose call strike at percentile( expected upside ) to finance put.
  - Put Spread: if severe tail probability low; reduce premium outlay.
  - Ratio Put / Tail Hedge (far OTM) for convexity if fat-tail probability elevated.
5. Present table: Expiry | Structure | Put Strike | Call Strike | Premium | Coverage% | Breakeven | Score.

### 20.4 Scenario Testing Pipeline
User picks scenario (slider or preset): Mild / Base / Severe / Tail.
1. Engine samples return path (Monte Carlo or deterministic shock).
2. Reprices portfolio & hedge pathwise.
3. Aggregates distribution metrics: P5 / Median / P95 final value; expected net payoff.
4. LLM generates comparative narrative:  
  “Under Severe scenario (−12% index), unhedged portfolio loss −$X (−Y%). Proposed collar limits loss to −$A (−B%) net of $premium with residual tail risk $R.”

### 20.5 Architecture Flow
```
Ingestion → Feature Store → (Vol Forecast | Regime | Event Impact | Tail MC) → Risk Window Aggregator
    → Strategy Recommender → Expiry/Strike Optimizer → Scenario Simulator → LLM Narrator → API/UI
```

### 20.6 Building Steps
1. Data Layer: implement scheduled fetchers (celery/cron) storing normalized events & OHLCV into time-series DB.
2. Feature Store: maintain rolling windows (returns, realized vol, skew, beta drift, correlation matrices).
3. ML Training Jobs: periodic retrain (weekly) – version & persist serialized models.
4. Real-Time Scoring: lightweight service updates risk windows when material events arrive.
5. Strategy Engine: implement modular hedge structures; cost model from live option chain (mid or model price if illiquid).
6. Scenario Simulator: vectorized Monte Carlo with variance-covariance + jump overlays; integrate Greeks for path-approx.
7. LLM Orchestration: prompt templates injecting quantitative tables; guardrails for compliance language.
8. API Endpoints:
  - `GET /api/insurance/opportunities` (list active upcoming uncertainty windows + top strategies)
  - `POST /api/insurance/scenario` (payload: positions, strategy_id, scenario_params)
9. UI Components: dashboard cards (Uncertainty Window, Suggested Hedge), expandable scenario panel, cost slider.
10. Feedback Loop: capture user acceptance / rejection to refine ranking model (implicit preference learning).

### 20.7 Investor Workflow
1. Observe “Upcoming Uncertainty” card (e.g. *FOMC + Elevated Volatility Regime*).
2. Review recommended strategies (cost vs coverage gauges).
3. Run custom scenario (change shock magnitude or duration).
4. Accept preferred hedge → auto-creates draft policy → bind executes orders.
5. Monitor live effectiveness chart (Portfolio vs Floor vs Hedged Curve).
6. Receive proactive alert if hedge delta deteriorates (roll suggestion).

### 20.8 Opportunity Framing
Output splits into two panels:
*Uncertainty:* Drivers, probability bands, projected drawdown distribution.
*Opportunity:* Cost-efficient hedge shortlist, potential premium rebate (collar), expected improvement in tail VaR.

### 20.9 Metrics & KPIs
| Metric | Definition |
|--------|------------|
| Hedge Cost Efficiency | (Unhedged ES – Hedged ES) / Premium |
| Hit Rate | % windows where realized drawdown entered predicted band |
| Over-Hedge Ratio | Premium spent when realized drawdown < threshold |
| User Adoption | # policies bound per recommended opportunity |
| Drift Alerts | Count of hedges flagged for rebalancing |

### 20.10 Safety / Compliance Considerations
- Clearly label probabilities as estimates (non-guaranteed).
- Provide baseline scenario unhedged for comparison (avoid misleading implied guarantees).
- Enforce suitability checks for advanced structures (ratio spreads, tail options).
- Log all model outputs, prompts, and user selections for audit.

### 20.11 Extensibility
- Multi-asset overlay (FX, rates futures) for cross-hedge efficiency.
- Reinforcement learning to adapt strike spacing from realized vs predicted outcomes.
- Adaptive premium budget allocator across concurrent uncertainty windows.

### 20.12 Minimal Prototype Slice
1. Implement volatility forecast + event calendar fusion → produce 1–2 upcoming windows.
2. Map to nearest two expiries; compute protective put & collar costs.
3. Simple Monte Carlo (normal + one jump) for scenario statistics.
4. LLM prompt summarizing 1 window & 2 strategies.
5. UI card + “Hedge Now” button → builds existing policy draft.

---
**Result:** Investors see not just reactive insurance but *forward-looking* hedging opportunities framed in plain language, with quantitative justification and scenario transparency.
