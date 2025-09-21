# Analyst Analysis Guide

## 1. Purpose of This Document
This guide explains everything available to an Analyst inside the platform for market, event, news, model and risk analysis. It covers data sources, dashboards, predictive intelligence, model recommendations, workflow best practices, and troubleshooting. Use it as a practical playbook for daily analytical operations.

---
## 2. Core Analyst Objectives Supported
| Objective | Supported Features |
|-----------|--------------------|
| Rapid situational awareness | Live Events & News Feed, Volatility Context (VIX), Real‑time Alerts |
| Forward-looking insight | Predictive Event Window (up to 15 days), Probability & Impact Heuristics |
| Model-driven edge | ML Model Recommendation Engine (alpha / risk / macro / hedge) |
| Risk posture monitoring | Volatility regime detection, Risk model suggestions, Compliance realtime feed |
| Research enrichment | AI Research Assistant, Knowledge Base Integration, Agentic AI Assistant |
| Collaboration & accountability | Analyst Assignments, Sessions, Certificates, Published Models Registry |
| Performance & iteration | Model Performance Tracking, Export + JSON snapshots |

---
## 3. Key Dashboards & Modules
| Module / Route | Purpose | Analyst Action |
|----------------|---------|----------------|
| `/events_analytics` | Baseline events/news listing | Quick scan & triage |
| `/enhanced_events_analytics` | Predictive + model intelligence layer | Deep dive & forward planning |
| `/ai_research_assistant` | Multi-source research & synthesis | Ask structured queries, build briefs |
| `/agentic_ai` | Autonomous task orchestration (agent flows) | Delegate repetitive analysis tasks |
| `/published` | Published ML models & artifacts | Review, reuse, validate |
| `/wealth_data_lake` | Broader financial datasets | Source factors & enrichment features |
| `/analyst/research_assignments` | Task allocation & progress | Accept / update / complete tasks |
| `/api/enhanced/market_dashboard` | JSON endpoint for composite dashboard | Programmatic pull or notebook integration |
| `/api/proxy/events_news` | Unified external feed (Sensibull + Upstox + VIX) | Use for lightweight data ingestion |

---
## 4. Data Sources & Normalization Pipeline
| Source | Content | Normalization Highlights |
|--------|---------|--------------------------|
| Sensibull (`/v1/current_events`) | Macro & market events (structured) | Flatten geographic & impact fields; unify timestamps |
| Upstox News API | Broad Indian market news headlines | Headline + summary mapped to unified `news` type |
| YFinance `^INDIAVIX` | Volatility context | Level, day-over-day change, trailing close series |
| Internal Mock (Fallback) | Resilience & offline mode | Injected only when externals fail |
| Predictions (Heuristic / Stub / Full) | Upcoming event candidates | Probability & confidence scores |

Normalization Goals:
1. Unified schema: `id`, `title`, `summary/description`, `category`, `impact (numeric/logical)`, `published_at (UTC-aware)`, `type`.
2. Timezone standardization: All timestamps converted or coerced to UTC.
3. Impact harmonization: qualitative (low/medium/high) → numeric scale for sorting & modeling.

---
## 5. Enhanced Events & Predictive Layer
| Element | Description | Analyst Use |
|---------|-------------|------------|
| Live Feed | Merged events + news sorted by recency | Rapid triage of catalysts |
| Upcoming Predictions (≤ 15 days) | Heuristic or model-derived forward events | Scenario prep & hedging decisions |
| Probability | 0–0.95 capped; volatility-adjusted | Prioritize >0.6 probability with high impact |
| Confidence | Heuristic confidence (low/med/high bands) | Filter low-confidence noise |
| Impact (Predicted) | 1–5 scale | Cross with portfolio exposure sensitivity |
| Volatility Context | VIX level, change, trailing series | Detect regime shifts / adapt sizing |
| Analyzer Mode Flag | `full`, `stub`, `none`, `error` | Trust level of advanced insights |
| Model Recommendations | Ranked list with rationale | Construct alpha + risk mitigation stack |

Modes:
- `full`: Full predictive engine active (ML capable).
- `stub`: Lightweight placeholder (structural continuity; conservative suggestions).
- `none`: Fallback sample only; do NOT rely for forward risk views.
- `error`: Investigation required (check logs / dependencies).

---
## 6. Model Recommendation Engine
Models are categorized for clarity:
| Category | Purpose | Example Models |
|----------|---------|----------------|
| macro | Regime / policy / growth inference | Macro Inflation Nowcast, Policy Rate Impact |
| alpha | Return generation targeting factor / event edges | Options Skew Arbitrage, Earnings Surprise GB |
| risk | Drawdown & volatility containment | Volatility Regime Classifier, Commodity Spillover |
| hedge | Protective overlays (future extension) | Tail Hedge Basket (planned) |

Each model descriptor includes:
- `expected_alpha_range`: Typical net contribution window.
- `lookback_window` & `retrain_frequency`: Operational cadence.
- `features`: Core drivers / required inputs.
- `why`: Match explanation tying feed/predictions to model activation.

Selection Logic (Simplified):
1. Keyword triggers (inflation, fed, earnings, oil, growth, labor, volatility).  
2. Volatility elevation adds regime & skew strategies.  
3. Prediction diversity (multiple future events) can add cycle classification.  
4. TF-IDF (if `scikit-learn` available) refines ordering by semantic relevance.

Analyst Workflow:
1. Scan recommended list → tag candidate models for portfolio alignment.  
2. Validate data readiness (feature availability & freshness).  
3. Stage backtest (if not previously validated) or load existing performance record.  
4. Size deployment factoring current volatility & conviction (probability × confidence).  
5. Log activation rationale (audit trail best practice).

---
## 7. Interpreting Volatility & Probability
| Signal | Analyst Action |
|--------|----------------|
| VIX < 15 (Calm) | Favor carry / mean-reversion models |
| VIX 15–20 (Neutral) | Balanced mix; monitor regime flips |
| VIX 20–30 (Elevated) | Introduce hedges, reduce gross exposure |
| VIX > 30 (Stress) | Prioritize risk models & tail protection |

Probability & Confidence Matrix:
| Prob | Confidence | Suggested Posture |
|------|-----------|-------------------|
| <40% | Any | Monitor only |
| 40–60% | Low/Med | Light positioning / alerts |
| 60–75% | Medium | Pre-position adaptively |
| >75% | High | Full preparation & scenario hedging |

---
## 8. Alerts & Fallback Behavior
| Trigger | Generated Alert |
|---------|-----------------|
| Elevated VIX (>20) | Volatility regime advisory |
| High-impact upcoming events | Sequencing risk notification |
| Analyzer in stub/none mode | Implicit reliability downgrade |

If proxy feed fails: system attempts legacy `/api/events/current` → mock data. Always verify analyzer_mode before acting on predictive panels.

---
## 9. Data Export & Reproducibility
- Download dashboard JSON via Export button (captures events, predictions, models, timestamps).  
- Store snapshots alongside research notes for later variance attribution.  
- For programmatic workflows: poll `/api/proxy/events_news` and `/api/predict_events?days=15` at controlled intervals (≥60s recommended to respect external API constraints).

---
## 10. Portfolio Integration Playbook
| Step | Action | Output |
|------|--------|--------|
| 1 | Collect current feed + predictions | Situation map |
| 2 | Filter events by portfolio exposure relevance | Focus list |
| 3 | Map suggested models to coverage gaps | Candidate roster |
| 4 | Stress test (what-if on high-impact events) | Risk deltas |
| 5 | Size + stage orders / hedges | Execution plan |
| 6 | Log rationale & model parameters | Audit artifact |
| 7 | Post-event attribution (PnL vs expected) | Feedback loop |

---
## 11. Extending the System (Analyst Requests)
| Enhancement Type | How to Propose |
|------------------|----------------|
| New keyword trigger | Submit mapping: keyword → model rationale |
| Add model descriptor | Provide fields: name, category, expected_alpha_range, features, why |
| Additional data source | Specify endpoint + schema + refresh cadence |
| Prediction algorithm upgrade | Outline target horizon, required features, validation metric |

---
## 12. Limitations & Caveats
- Heuristic probabilities (unless full engine active) are NOT calibrated; use directionally.  
- External APIs may intermittently throttle; fallback data reduces breadth.  
- Stub analyzer mode is for UI continuity only—not production decisioning.  
- Model recommendations do not guarantee alpha; they prioritize investigation.  
- Impact scores are relative, not absolute macro magnitudes.

---
## 13. Troubleshooting Quick Table
| Symptom | Likely Cause | Analyst Action |
|---------|--------------|----------------|
| Empty feed | External API outage / network | Refresh after 60s; check diagnostics in JSON |
| analyzer_mode = none | Import / dependency failure | Notify engineering; avoid predictive reliance |
| No model recommendations | Low semantic triggers | Manually review event keywords |
| Repeated stub models | Full analyzer dependencies missing | Install / enable full ML stack (engineering) |

---
## 14. Best Practice Checklist
- [ ] Confirm analyzer_mode == full before heavy predictive usage.  
- [ ] Cross-check top 3 high-probability events with independent sources.  
- [ ] Document rationale for each activated model.  
- [ ] Adjust sizing when VIX crosses regime thresholds.  
- [ ] Export daily snapshot for audit & attribution.  
- [ ] Review stale predictions older than 48h.  

---
## 15. Glossary (Selected)
| Term | Definition |
|------|------------|
| Impact | Relative event effect scale (1–5) or low/medium/high mapped numerically |
| Probability | Heuristic likelihood of scheduled event materializing / affecting markets |
| Confidence | Qualitative reliability indicator for the probability estimate |
| VIX | India volatility index used as regime proxy |
| Model Descriptor | Structured metadata for recommended ML approach |
| Regime | Macro/volatility state influencing strategy suitability |
| Stub Mode | Lightweight fallback analytics implementation |

---
## 16. Quick API Reference
| Endpoint | Use |
|----------|-----|
| `/api/proxy/events_news` | Unified real-time events + news + VIX + predictions + model_rec |
| `/api/predict_events?days=15` | 15‑day forward prediction window |
| `/api/enhanced/market_dashboard` | Composite market + analytics snapshot |
| `/api/enhanced/event_analysis` (POST) | Detailed analysis for a single event |
| `/api/enhanced/recommend_models` (POST) | Model recommendations for supplied event/prediction |

---
## 17. Contact & Escalation
| Issue Type | Contact |
|------------|--------|
| Data integrity / missing events | Data Engineering |
| Model recommendation quality | Quant / ML Team |
| UI / dashboard errors | Frontend Engineering |
| API failures / 5xx | Backend Engineering |
| Compliance / audit trail | Compliance Ops |

---
## 18. Revision Roadmap (Planned Enhancements)
| Planned | Description |
|---------|-------------|
| Calibrated probability models | Replace heuristic with historical feature-trained classifier |
| Tail risk hedge module | Dynamic hedge sizing suggestions |
| Cross-asset correlation lens | Event impact propagation analysis |
| Analyst annotation layer | Shared tagging & commentary for events |
| Scenario simulation engine | Replay historical analog events |

---
**Usage Disclaimer:** This platform augments but does not replace professional judgment. Always corroborate automated insights with independent validation.

*End of Guide.*
