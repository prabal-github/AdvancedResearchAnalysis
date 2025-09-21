# Financial Analyst Talent Hunt — Evaluation Framework

This document explains how the existing application evaluates Research Analysts during the Talent Hunt and how internship selections are made. It reflects the logic implemented in the current codebase (scoring pipeline, UI dashboards, and compliance checks).

## What we evaluate

Each submitted research report is analyzed and scored. Scores then roll up into analyst-level performance metrics used for shortlisting and internship offers.

High-level goals:
- Reward research quality, clarity, rigor, and compliance.
- Discourage low‑effort, AI‑generated or plagiarized content.
- Encourage actionable, well-justified recommendations with balanced risk.

## How report scoring works (in the app)

Source: `models/scoring.py` (class `ResearchReportScorer`) and analyst dashboards (`templates/analyst_performance.html`, `templates/public_report.html`).

For each report, the system computes a Base Composite Score from multiple components, then applies penalties (plagiarism and AI-detection) to produce the final Composite Quality Score.

### Components and weights (Base Composite Score)

Weights are expressed as a percentage of the base. All component scores are 0.0–1.0 unless noted.
- Factual Accuracy — 16%
- Predictive Power — 12%
- Bias Control (1 − |bias_score|) — 9%
- Originality — 9%
- Risk Disclosure — 11%
- Transparency — 7%
- Geopolitical Risk Assessment — 9%
- SEBI Compliance — 7%
- Content Quality Metrics (depth, citations, targets, timelines, risk mentions) — 5%
- Content Guidelines Compliance (balanced tone, justification, scenarios, timelines) — 5%
- Stock Quality Assessment (portfolio-level quality across covered tickers) — 10%

Then:
- Final Composite Quality Score = max(0, Base Composite − Plagiarism Penalty − AI Penalty)

### Signals and how they are measured

- Factual accuracy & transparency: presence of data sources, financial metrics, numeric evidence, and verification cues.
- Predictive power: simplified backtesting on covered tickers and trend consistency.
- Bias control: neutral language usage, balanced perspectives, acknowledgment of risks, scenario analysis.
- Originality: internal plagiarism checker score (lower plagiarism → higher originality).
- Risk disclosure: explicit risk mentions, specificity, and breadth.
- SEBI compliance (detailed): structured checks for disclosures, methodology, conflicts, disclaimers, etc. Includes an overall compliance score exposed in UI.
- Geopolitical assessment: mentions, context, and impact analysis for relevant macro/geopolitical factors.
- Content quality metrics: depth of financial/technical analysis, citations, price-target clarity, timelines, and risk mentions.
- Content guidelines compliance: methodology explained, assumptions stated, peer comparison, sensitivity, timelines.
- Stock quality assessment: ticker-level quality (technical/fundamental proxies) rolled into portfolio-level metrics and insights.

### Penalties (Quality gates)

- Plagiarism penalty: computed from the plagiarism score; subtracts from the base.
- AI-detection penalty: computed from the AI probability; subtracts from the base.
- Flagged alerts & action items: generated for compliance/quality issues and surfaced on dashboards to guide fixes.

### Data returned per report

The scorer returns a structured payload used by dashboards, including:
- `composite_quality_score` (0–1), `base_composite_score` (0–1)
- `scores` breakdown by component
- `plagiarism_score`, `plagiarism_penalty`, `ai_probability`, `ai_penalty`
- `backtest_results`, `sentiment_trend`
- `detailed_quality_metrics`, `content_guidelines_analysis`
- `sebi_compliance` and `sebi_compliance_detailed`
- `flagged_alerts`, `action_items`
- `stock_quality_assessment` (avg score, distribution, insights)

Key UI surfaces:
- Analyst Performance dashboard shows: report quality bars, AI detection badges, issue counts, SEBI averages, and trends.
- Public Report view shows: quality percentage, analyst metrics summary, and sharing options.

## Analyst-level performance metrics

Aggregated per analyst (visible in dashboards):
- Total Reports Published
- Average Quality Score (mean of `composite_quality_score` × 100%)
- Trend of quality (improving/declining)
- SEBI compliance (average of detailed overall scores)
- AI detection distribution (Human/Uncertain/AI badges)
- Issues flagged per report (from `flagged_alerts`)
- Portfolio/ticker insights taken from Stock Quality Assessment

These metrics update automatically as analysts submit reports.

## Internship selection criteria (Talent Hunt)

Recommended thresholds aligned with the current system:
- Minimum activity: ≥ 5 published reports during the Hunt window.
- Quality bar: Average Composite Quality Score ≥ 0.70 (70%).
- Compliance bar: Average detailed SEBI compliance ≥ 0.70.
- Integrity bar: 
  - Average plagiarism score < 0.20; no severe plagiarism incidents.
  - AI probability: At least 70% of reports tagged “Human” (ai_probability < 0.40), and none with high AI probability (> 0.70) without satisfactory human review.
- Reliability bar: Average flagged alerts ≤ 1 per report; no critical compliance alerts outstanding.
- Research rigor: 
  - Content Quality Metrics average ≥ 0.60.
  - Stock Quality Assessment average ≥ 0.60 (where applicable).

Tiebreakers when candidates are close:
- Higher originality (lower plagiarism), better risk disclosure, stronger transparency.
- Better SEBI detailed compliance and fewer unresolved action items.
- More consistent or improving quality trend across the window.

Notes:
- For new analysts with < 5 reports, treat as “probationary”; require additional submissions or a live assignment.
- All thresholds can be tuned per cohort and market regime; they’re meant as sensible defaults.

## Process flow (operational)

1) Report submission → System runs scoring pipeline automatically.
2) Dashboard updates:
   - Report card: quality bar, AI badge, issues, SEBI compliance, insights.
   - Analyst metrics: aggregates and trends.
3) Candidate monitoring:
   - Leaderboard/filters (by average score, compliance, volume).
   - Manual review of outliers, flagged alerts, and public sharables.
4) Shortlist & interviews:
   - Apply criteria above; perform short interviews and a live case if needed.
5) Internship offers:
   - Confirm identity and ethics policy; finalize offers.

## Where this lives in the code

- Scoring engine: `.../models/scoring.py` (class `ResearchReportScorer`)
  - Methods: `_calculate_quality_scores`, `_analyze_detailed_quality_metrics`, `_comprehensive_sebi_compliance_analysis`, `_analyze_content_guidelines`, `_assess_stock_quality`, backtesting/sentiment, and penalty functions.
- Analyst dashboards:
  - `templates/analyst_performance.html` — report tables, quality bars, AI badges, issues, SEBI averages.
  - `templates/analyst_profile.html` — recent reports with composite quality bars and AI badges.
  - `templates/public_report.html` — public summary with analyst stats and quality display.

## Appendix — Parameter overview

Scored components (0–1) and weights:
- Factual Accuracy — 16%
- Predictive Power — 12%
- Bias Control — 9%
- Originality — 9%
- Risk Disclosure — 11%
- Transparency — 7%
- Geopolitical Assessment — 9%
- SEBI Compliance — 7%
- Content Quality Metrics — 5%
- Content Guidelines Compliance — 5%
- Stock Quality Assessment — 10%

Penalties (subtract from base):
- Plagiarism Penalty (from plagiarism score)
- AI Penalty (from AI probability)

Outputs used in UI:
- `composite_quality_score` (final), `base_composite_score` (pre-penalty)
- SEBI detailed compliance and alerts/action items
- AI and plagiarism indicators
- Backtesting and sentiment summaries
- Stock quality insights

This framework provides a fair, transparent, and enforceable standard to identify top-performing research analysts for internship opportunities.
