# Usage & Plans Guide

This document explains how to run the application locally, core URLs, API usage, and the plans/quotas model for investors and analysts.

## Quick start

Prerequisites
- Python 3.9+
- Windows/macOS/Linux

Steps
1) Create and activate a virtual environment
2) Install dependencies from `requirements.txt`
3) Run the app entrypoint `python app.py`
4) Open the app in your browser (default http://127.0.0.1:5000/)

Notes
- Default DB is SQLite at `investment_research.db` (see `config.py`).
- The app auto-creates tables on first run if missing.
- A VS Code task "Run Flask App" is available to start the server.

## Core configuration

File: `config.py`
- SQLALCHEMY_DATABASE_URI: default `sqlite:///investment_research.db`
- DEBUG: default `True`
- LLM_MODEL: default `"mistral:latest"`
- LLM_PORT: default `8000`
- Optional GitHub settings: placeholders for token/user/repo prefix

Optional integrations (install the package to enable)
- Anthropic (Claude): `anthropic`
- Report generation: `reportlab`
- GitHub API: `PyGithub`
- BERT-based NLP: `transformers` and `torch`
- HTTP cache: `requests_cache`

If a package is not installed, related features gracefully disable.

## User flows and URLs

Home
- `/` Home/Landing

Investor
- `/investor_register` Register
- `/investor_login` Login
- `/investor_dashboard` Dashboard
- `/investor_logout` Logout
- `/investor/risk_profile` Risk profile
- `/portfolio` Portfolio UI

Analyst
- `/register_analyst` Register
- `/analyst_login` Login
- `/analyst_dashboard` Dashboard
- `/analyst_logout` Logout
- `/analyst/submit_report` Submit report
- `/analyst/performance_dashboard` Performance

Admin
- `/admin_login` Login
- `/admin_dashboard` Dashboard
- `/admin/usage_plans` Manage plans/quotas
- `/admin/investor_registrations` Approvals
- `/admin/create_investor`, `/admin/create_analyst` Create users
- `/admin/manage_analysts` Manage analysts

AI and analysis
- `/ai_research_assistant` Web UI
- `/report_hub` Reports hub

Selected APIs
- `GET /api/main_dashboard`
- `GET /api/investor_dashboard`
- `GET /api/enhanced_analysis_reports` (and `/api/enhanced_analysis_reports/<ticker>`) 
- `POST /api/ai_research_assistant`
- `GET /api/admin/performance`
- `GET /api/metrics`

## Plans and quotas

Two roles with tiers and rate limits. Defaults on registration: Investors = `retail`, Analysts = `small`.

Hourly quotas
- Investor
  - retail: 120/hour
  - pro: 1200/hour
  - pro_plus: 5000/hour
- Analyst
  - small: 240/hour
  - pro: 2400/hour
  - pro_plus: 8000/hour

Daily caps (entry tiers)
- investor: retail = 300/day
- analyst: small = 600/day

Weighted path costs (examples)
- Dashboards: `/investor_dashboard`, `/analyst_dashboard` cost 10 units
- Advanced/sector-heavy pages: 12 units
- Portfolio operations: ~8 units
- Many API calls: ~4 units

Notes
- See `PATH_COSTS` and `ROLE_TIERS` near the top of `app.py` for the authoritative values.
- APIs and pages consume quota based on their path weight. If you exceed hourly or daily limits, a 429 response is returned.
- "Soft-limit" behavior is enabled for key dashboards (see `SOFT_LIMIT_PATHS` in `app.py`): the page attempts to render a reduced experience instead of hard-blocking.

Plan upgrade/downgrade
- Users can request an upgrade at `/request_upgrade`.
- Admins adjust plans via `/admin/usage_plans` and `/admin/update_plan`.

## Optional AI/ML integrations

Local/hosted LLM
- Ensure your local LLM server matches `LLM_MODEL` and `LLM_PORT` in `config.py` (default `mistral:latest` on port 8000).

Anthropic
- Install `anthropic` and provide your API key as an environment variable if used; code automatically enables enhanced responses when the package is available.

BERT-based checks
- Install `transformers` + `torch` to enable BERT plagiarism/AI-detection paths. Without these, the app uses fallback heuristics or disables those features.

Report PDFs
- Install `reportlab` for certificate/report PDF generation.

GitHub integration
- Install `PyGithub` and fill in the GitHub config in `config.py` if you intend to use repository features.

## Data and sample content

Useful scripts (optional)
- `create_admin_account.py` Create an admin user
- `create_demo_accounts.py` Seed sample investors/analysts
- `create_sample_dashboard_data.py`, `create_sample_recommendations.py` Populate dashboards
- `create_scenario_tables.py` Initialize scenario/backtest tables

Run these with the app stopped. Review each script before running.

## Troubleshooting

- ImportError for optional packages: Install the missing package or ignore if you don't need that feature.
- LLM not responding/timeouts: Verify your LLM server is running at `LLM_PORT` and model name matches `LLM_MODEL`.
- SQLite lock or schema issues: Stop the server and run `check_db_schema.py` or `fix_database` route. Consider deleting the local DB for a fresh start in development.
- 429 Too Many Requests: You've hit your plan quota. Wait for the hourly window reset or request an upgrade.
- Socket issues on Windows: Ensure no firewall is blocking localhost:5000; retry with a clean venv.

## Security and access

- Admin pages require admin authentication. Use `create_admin_account.py` to bootstrap an admin.
- Uploaded scripts run only in admin-restricted areas with strict file/type/timeouts; do not enable for untrusted users.

## Where to look in code

- `app.py` — Main app, routes, rate limiting (ROLE_TIERS, DAILY_LIMITS, PATH_COSTS, SOFT_LIMIT_PATHS), models
- `config.py` — Configuration values
- `templates/` and `static/` — UI
- `requirements.txt` — Dependencies

## Appendix: API quick checks

Examples (use an authenticated session when required):
- `GET /api/main_dashboard`
- `GET /api/investor_dashboard`
- `GET /api/enhanced_analysis_reports?sector=technology`
- `POST /api/ai_research_assistant` with JSON body `{ "query": "Analyze AAPL earnings" }`

