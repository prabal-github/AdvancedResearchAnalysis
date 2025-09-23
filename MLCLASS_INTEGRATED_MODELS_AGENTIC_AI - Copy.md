# VS Terminal ML Class – Integrated & Extensible ML Models + Agentic AI Suite

Endpoint Context: http://127.0.0.1:80/vs_terminal_MLClass
Primary Audience: Investor-facing analytical & decision-support workflows (portfolio insight, risk, optimization, research automation, trade intelligence, compliance awareness).

---

## 1. Current Integrated ML (Logical) Models

(Implemented as heuristic / placeholder logic today; structured for future real ML backends.)

| Model Key             | Purpose                        | Core Features (Current)       | Planned Upgrade Path                          | Example Output Fields                       |
| --------------------- | ------------------------------ | ----------------------------- | --------------------------------------------- | ------------------------------------------- |
| stock_price_predictor | Short-horizon price projection | Simple % drift + random noise | LSTM / Temporal Fusion / Prophet ensemble     | projected_price, confidence, expected_range |
| risk_classifier       | Portfolio risk bucket          | Heuristic volatility score    | Historical VaR / CVaR + factor betas          | risk_score, risk_classification             |
| sentiment_analyzer    | Aggregate market tone          | Static neutral scoring        | FinBERT / domain LLM + news & social feeds    | overall_sentiment, sentiment_score          |
| anomaly_detector      | Detect unusual moves           | Std-dev threshold             | Isolation Forest / AE / Z-score multi-factor  | anomalies[], anomaly_score                  |
| portfolio_optimizer   | Allocation suggestion          | Naive weight shift            | Mean-Variance / Black-Litterman / Risk Parity | suggested_weights, rationale                |

### Input Contract (Generic ML Model Invocation)

```json
{
  "model_id": "stock_price_predictor",
  "portfolio_id": "portfolio_1",
  "symbols": ["RELIANCE", "TCS", "HDFCBANK"],
  "context": { "horizon_minutes": 240 }
}
```

### Output Contract (Generic)

```json
{
  "success": true,
  "model": "stock_price_predictor",
  "run_id": "mlrun_20250911_123455",
  "results": [
    { "symbol": "RELIANCE", "projected_price": 2540.7, "confidence": 0.62 }
  ],
  "meta": { "horizon_minutes": 240, "generated_at": "2025-09-11T08:04:11Z" },
  "summary": "Moderate bullish drift expected; watch resistance near 2555."
}
```

---

## 2. Current Agentic AI Suite (Autonomous Roles)

| Agent                         | Role Focus                            | Core Current Logic         | Near-Term Enhancement                                   |
| ----------------------------- | ------------------------------------- | -------------------------- | ------------------------------------------------------- |
| Portfolio Risk Agent          | Monitors exposure & volatility        | Simple heuristics          | Realized/Implied vol, VaR drift, alert thresholds       |
| Trading Signals Agent         | Generates tactical entry/exit signals | Placeholder momentum flags | Multi-factor strategy graph + confidence blending       |
| Market Intelligence Agent     | Macro / sector / event summarization  | Static templated output    | Streaming macro feed summarization + regime shifts      |
| Compliance Monitoring Agent   | Rule / restriction awareness          | Hard-coded rule checks     | RegTech rule engine + watchlist integration             |
| Client Advisory Agent         | Portfolio narrative explanations      | Template responses         | LLM w/ retrieval over investor profile + market context |
| Performance Attribution Agent | Source of returns & contributions     | Weighted contribution math | Multi-period Brinson attribution & factor attribution   |
| Research Automation Agent     | Draft structured research insights    | Patterned summary          | Multi-document retrieval + structured report generator  |

### Generic Agent Invocation Contract

```json
{
  "agent_id": "portfolio_risk",
  "portfolio_id": "portfolio_1",
  "symbols": ["RELIANCE", "TCS"],
  "mode": "snapshot", // or "monitor", "explain"
  "parameters": { "lookback_days": 30 }
}
```

### Generic Agent Response

```json
{
  "success": true,
  "agent": "portfolio_risk",
  "analysis": { "risk_score": 6.1, "volatility_flag": "elevated" },
  "recommendations": ["Consider reducing concentration in RELIANCE"],
  "timestamp": "2025-09-11T08:08:22Z"
}
```

---

## 3. UI Integration Touchpoints (vs_terminal_MLClass)

| UI Section                   | Backend Endpoint                               | Data Type                                | Frequency                  | Notes                                     |
| ---------------------------- | ---------------------------------------------- | ---------------------------------------- | -------------------------- | ----------------------------------------- |
| Real-Time Insights Tab       | `/api/vs_terminal_MLClass/realtime_insights`   | Aggregated quotes, risk stats, forecasts | On demand / refresh button | Expand with websocket streaming later     |
| ML Predictions Panel         | `/api/vs_terminal_MLClass/ml_predictions`      | Array of model outputs                   | User trigger               | Add batch run + export                    |
| Live Chart (Explain)         | `/api/vs_terminal_MLClass/chart_explain`       | HTML AI technical narrative              | User button                | Providers: Anthropic → Ollama → heuristic |
| AI Chat Assistant            | `/api/vs_terminal_MLClass/chat`                | Conversational classification + guidance | Freeform                   | Extend to RAG over portfolio history      |
| Agent Tasks (Future Sidebar) | `/api/vs_terminal_MLClass/agent_run` (planned) | Structured agent response                | On request / schedule      | Consolidated run orchestrator             |

---

## 4. Recommended Next ML Models (Investor Value Prioritized)

| Priority | Model                                  | Rationale                               | Core Inputs                            | Key Outputs                   |
| -------- | -------------------------------------- | --------------------------------------- | -------------------------------------- | ----------------------------- |
| High     | Volatility Forecaster (GARCH / EGARCH) | Improves risk metrics & position sizing | Price series                           | forecast_vol, conf_interval   |
| High     | Factor Exposure Estimator              | Factor-aware attribution & hedging      | Returns series, factor returns         | betas{}, factor_contrib[]     |
| Medium   | Regime Classifier (HMM / Clustering)   | Contextualizes signals & risk           | Macro & index features                 | regime_label, transition_prob |
| Medium   | Event Impact Model                     | Earnings/news shock assimilation        | Corporate events, historical reactions | expected_gap, decay_curve     |
| Medium   | ESG Scoring Integrator                 | Compliance / sustainable mandates       | ESG feed & portfolio                   | esg_score, controversy_flags  |
| Low      | Options Greeks Estimator               | Derivatives overlay                     | Option chain snapshot                  | greeks{}, iv_surface_summary  |
| Low      | Liquidity Stress Simulator             | Drawdown resilience                     | Depth/volume stats                     | stress_loss_scenarios[]       |

---

## 5. Recommended Additional Agents

| Agent                  | Purpose                                | Inputs                            | Outputs                               | Special Considerations          |
| ---------------------- | -------------------------------------- | --------------------------------- | ------------------------------------- | ------------------------------- |
| Macro Regime Agent     | Detect & broadcast macro regime shifts | Economic indicators, yield curves | regime_state, confidence              | Weekly & on event triggers      |
| Hedging Strategy Agent | Suggest hedge overlays                 | Portfolio exposures, vol forecast | hedge_candidates[], cost_estimate     | Uses factor betas + vol model   |
| ESG Compliance Agent   | Continuous ESG screening               | Portfolio holdings, ESG feed      | violations[], score_drift             | Update on quarterly ESG refresh |
| Tax Optimization Agent | Harvest & deferral scenarios           | Trade history, unrealized P/L     | harvest_candidates[], tax_savings_est | Jurisdiction rules needed       |
| Corporate Action Agent | Anticipate mandatory/optional actions  | Corporate action calendar         | action_alerts[], response_window      | Integrate with external CA API  |
| News Impact Agent      | Rapid sentiment & risk ranking         | News headlines stream             | impact_assessments[]                  | Latency-sensitive, caching      |

---

## 6. Architecture Layering

```
[ UI / vs_terminal_MLClass ]
   |--(REST calls)-->  [ Flask Controller Layer ]
                          |-- Model Orchestrator (routing, batching)
                          |-- Agent Controller (multi-agent prompts, state)
                          |-- Data Access Layer (quotes, histories, fundamentals)
                          |-- Caching (in-memory LRU + optional Redis)
                          |-- Provider Abstraction (Anthropic / Ollama / Future OpenAI)
```

### Integration Flow (Example: Chart Explain)

1. UI button → POST `/chart_explain` with {symbol}
2. Fetch OHLC (yfinance or synthetic)
3. Compute lightweight indicators
4. Build structured prompt
5. Try Anthropic Sonnet 3.5 → fallback Ollama → fallback heuristic
6. Return HTML summary + provider tag
7. UI renders summary with provider badge.

---

## 7. Standardized Endpoint Patterns

| Pattern                              | Method   | Purpose                                | Status Code Semantics                            |
| ------------------------------------ | -------- | -------------------------------------- | ------------------------------------------------ |
| `/api/vs_terminal_MLClass/<feature>` | POST     | Execute model/agent or fetch analytics | 200 success / 400 bad input / 500 internal error |
| `/api/.../realtime_*`                | GET/POST | Mixed real-time aggregation            | 200 data / 206 partial / 500 error               |

### Error Envelope

```json
{ "success": false, "error": "description", "trace_id": "opt" }
```

---

## 8. Data Contracts (Key Objects)

### Quote Object

```json
{
  "symbol": "RELIANCE",
  "price": 2541.25,
  "change_pct": 0.47,
  "time": "2025-09-11T08:10:00Z"
}
```

### Forecast Object

```json
{
  "symbol": "RELIANCE",
  "model": "stock_price_predictor",
  "projected": 2555.4,
  "confidence": 0.61,
  "horizon_min": 240
}
```

### Risk Stats Object

```json
{
  "symbol": "RELIANCE",
  "risk_score": 6.2,
  "volatility_est": 0.23,
  "flags": ["elevated_vol"]
}
```

---

## 9. Security & Auth Considerations

| Component            | Current                         | Recommended Upgrade                                |
| -------------------- | ------------------------------- | -------------------------------------------------- |
| Chat / Chart Explain | Partially open for chart prompt | API key or session token gating with rate limiting |
| Agent Runs           | Session based                   | Fine-grained RBAC (analyst vs investor)            |
| Model Access         | Open heuristics                 | Quota + audit logging per investor                 |

---

## 10. Logging & Observability

| Layer              | Metrics                         | Suggested Implementation              |
| ------------------ | ------------------------------- | ------------------------------------- |
| Model Orchestrator | latency_ms, success_ratio       | Prometheus counters/gauges            |
| Agent Controller   | agent_exec_time, retries        | Structured JSON logs                  |
| Provider Layer     | provider_latency, fallback_rate | Wrap API calls with timing decorators |
| UI Actions         | feature_usage counts            | JS beacon → /analytics endpoint       |

---

## 11. Caching Strategy

| Data                             | TTL               | Invalidation        |
| -------------------------------- | ----------------- | ------------------- |
| Intraday quotes                  | 5–10s             | Time-based only     |
| Indicators (per symbol/interval) | 30–60s            | On explicit refresh |
| Agent snapshot outputs           | 1–5m              | On portfolio change |
| Model predictions                | Horizon-dependent | On new run request  |

---

## 12. Roadmap Milestones

| Phase   | Deliverables                                             | Success Criteria                                 |
| ------- | -------------------------------------------------------- | ------------------------------------------------ |
| Phase 1 | Normalize existing heuristics behind service interfaces  | All current models behind `ModelService` pattern |
| Phase 2 | Add volatility + factor models                           | Accurate beta & vol vs benchmarks (backtest)     |
| Phase 3 | Introduce macro regime + hedging agents                  | Regime label accuracy > baseline clustering      |
| Phase 4 | Replace sentiment placeholder with live feed LLM scoring | Latency <2s per headline batch                   |
| Phase 5 | Deploy optimization with real constraints                | Portfolio weight proposals pass compliance tests |

---

## 13. Example Unified Response (Future Aggregated Endpoint)

```json
{
  "portfolio_id":"portfolio_1",
  "snapshot_ts":"2025-09-11T08:12:42Z",
  "quotes":[...],
  "risk": {"overall_score": 6.0, "top_drivers": ["RELIANCE", "TCS" ]},
  "signals": {"long": ["TCS"], "watch": ["HDFCBANK"], "confidence_map": {"TCS":0.64}},
  "forecast": {"1d_drift_pct": 0.45, "vol_forecast": 0.22},
  "regime": {"label":"late_cycle_slowing", "confidence":0.58},
  "optimization": {"suggested_rebalance": [{"symbol":"RELIANCE","target_w":0.18}]},
  "ai_summary": "Portfolio exhibits mild positive momentum with concentrated risk in large-cap financials; consider incremental diversification into defensives."
}
```

---

## 14. Integration Steps to Add a New Model

1. Define contract in `model_registry` (id, description, expected inputs, output fields).
2. Implement adapter class (e.g., `FactorExposureModel`) with `run(symbols, params)`.
3. Register in central dispatcher (e.g., dictionary in `app.py`).
4. Expose via `/api/vs_terminal_MLClass/ml_predictions` option.
5. Update UI model selection list.
6. Add lightweight test with synthetic input.
7. Add caching layer if heavy compute.

---

## 15. Integration Steps to Add a New Agent

1. Create agent class with `analyze(context)` returning structured dict.
2. Add to `AgenticAIMasterController` registry.
3. (Optional) Add scheduled job / polling if continuous monitoring.
4. Expose REST endpoint `/api/vs_terminal_MLClass/agent_run` with `agent_id`.
5. Extend UI: New tab or integrated panel.
6. Provide AI summary mapping (convert structured data → narrative).

---

## 16. Provider Abstraction (Anthropic + Ollama)

| Provider             | Use Cases                                         | Fallback Rules                       | Config                  |
| -------------------- | ------------------------------------------------- | ------------------------------------ | ----------------------- |
| Anthropic Sonnet 3.5 | High-quality analytical narratives (chart, macro) | If API key missing or error → Ollama | `ANTHROPIC_API_KEY` env |
| Ollama (llama3)      | Local dev & fallback                              | If unavailable → heuristic template  | Local daemon port 11434 |

Recommended enhancement: Introduce `ProviderRouter` with weighted selection & health probing.

---

## 17. Heuristic → ML Migration Strategy

| Component         | Current        | Target                                          | Requirement                    |
| ----------------- | -------------- | ----------------------------------------------- | ------------------------------ |
| Drift Forecast    | Random drift   | Time-series ensemble                            | Historical bar store           |
| Risk Score        | Simple scaling | Multi-factor + VaR                              | Return matrix + factor data    |
| Sentiment         | Static         | Streaming LLM scoring                           | News ingestion microservice    |
| Optimization      | Naive weights  | Constrained optimizer (PyPortfolioOpt / custom) | Covariance matrix + risk model |
| Anomaly Detection | Std-dev        | Isolation Forest / Autoencoder                  | Feature engineering pipeline   |

---

## 18. Testing & Validation

| Layer             | Test Type   | Example                             |
| ----------------- | ----------- | ----------------------------------- |
| Indicator Engine  | Unit        | RSI correctness on synthetic series |
| Model Dispatcher  | Unit        | Unknown model id → 400              |
| Agent Response    | Schema      | Validate required keys present      |
| Provider Fallback | Integration | Force Anthropic error → uses Ollama |
| Performance       | Benchmark   | Latency < 1.5s for 5 symbols ML run |

---

## 19. Minimal Code Skeleton for New Model

```python
class FactorExposureModel:
    id = "factor_exposure"
    description = "Estimate portfolio exposures to style & sector factors"
    def run(self, symbols, params=None):
        # TODO: fetch historical returns & factor returns
        exposures = {s: {"value": 0.0, "growth": 0.0, "quality": 0.0} for s in symbols}
        return {"model": self.id, "exposures": exposures, "meta": {"days": 90}}
```

---

## 20. Quick Start (Local Dev)

1. Set `ANTHROPIC_API_KEY` (optional for premium summaries).
2. (Optional) Start Ollama: `ollama run llama3`.
3. Launch Flask: `python app.py` (ensure port 80).
4. Open UI: http://127.0.0.1:80/vs_terminal_MLClass
5. Use Live Chart → AI Explain to test provider cascade.

---

## 21. Suggested Immediate Next Steps

| Rank | Action                                                | Impact                            |
| ---- | ----------------------------------------------------- | --------------------------------- |
| 1    | Normalize model registry & implement dispatcher class | Reduces coupling                  |
| 2    | Add volatility & factor models                        | Improves risk / attribution depth |
| 3    | Implement Agent Run endpoint                          | Enables UI agent tasks panel      |
| 4    | Introduce caching + provider health checks            | Stability & latency               |
| 5    | Replace sentiment placeholder                         | Higher investor trust             |

---

## 22. Glossary

| Term   | Definition                                                           |
| ------ | -------------------------------------------------------------------- |
| VaR    | Value at Risk: statistical loss threshold at confidence over horizon |
| Regime | Macro/market structural state affecting return distributions         |
| Factor | Systematic risk/return driver (value, momentum, size, quality, etc.) |
| Drift  | Expected small directional move absent shocks                        |

---

## 23. Contact / Ownership

| Domain        | Owner    | Notes                        |
| ------------- | -------- | ---------------------------- |
| Model Infra   | (assign) | Registry, execution, caching |
| Agent Logic   | (assign) | Multi-agent frameworks       |
| Data Feeds    | (assign) | Quotes, fundamentals, news   |
| LLM Providers | (assign) | Keys, routing, fallback      |

---

Document Version: 1.0 (Generated 2025-09-11)
