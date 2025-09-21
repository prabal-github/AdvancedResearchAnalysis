# Stock Analysis Publish & Permission Flow (Analyst → Investor)

This guide shows (A) how the Analyst loads and publishes code (including a safe public function `add`) and (B) how an Investor requests edit access to extend functionality (e.g. add new stocks). All steps map to existing UI panels in `vs_terminal` and REST endpoints.

---
## 1. Analyst: Prepare Code in VS Terminal
Load (paste) the following code into the main editor in `/vs_terminal`.

```python
# -*- coding: utf-8 -*-
import yfinance as yf

# Safe public demo function (simple, deterministic)
def add(a, b):
    return a + b

def calculate_intrinsic_value(fcf, growth_rate, discount_rate, terminal_growth_rate, years, shares_outstanding):
    discounted_fcfs = []
    for year in range(1, years + 1):
        projected_fcf = fcf * ((1 + growth_rate) ** year)
        discounted_fcf = projected_fcf / ((1 + discount_rate) ** year)
        discounted_fcfs.append(discounted_fcf)
    terminal_fcf = fcf * ((1 + growth_rate) ** years)
    terminal_value = (terminal_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    discounted_terminal_value = terminal_value / ((1 + discount_rate) ** years)
    total_value_crores = sum(discounted_fcfs) + discounted_terminal_value
    equity_value_rupees = total_value_crores * 1e7  # Convert crores to INR
    intrinsic_value_per_share = equity_value_rupees / shares_outstanding
    return intrinsic_value_per_share

def _analyze_company_raw(ticker, company_name, assumptions):
    stock = yf.Ticker(ticker)
    try:
        current_price = stock.history(period='1d')['Close'][0]
    except Exception:
        return {"error": f"price fetch failed for {ticker}"}
    try:
        shares_outstanding = stock.info.get('sharesOutstanding')
    except Exception:
        shares_outstanding = None
    if not shares_outstanding:
        return {"error": f"shares outstanding missing for {ticker}"}
    intrinsic_value = calculate_intrinsic_value(
        assumptions['fcf'],
        assumptions['growth_rate'],
        assumptions['discount_rate'],
        assumptions['terminal_growth_rate'],
        assumptions['years'],
        shares_outstanding
    )
    status = "Undervalued" if intrinsic_value > current_price else "Overvalued"
    return {
        "company": company_name,
        "ticker": ticker,
        "price": float(current_price),
        "intrinsic_value": float(intrinsic_value),
        "status": status
    }

# Public wrapper: one-ticker analysis (narrow surface, safe to expose)
def analyze_one(ticker: str, fcf: float, growth_rate: float, discount_rate: float, terminal_growth_rate: float, years: int, company_name: str = "Company"):
    assumptions = {
        'fcf': fcf,
        'growth_rate': growth_rate,
        'discount_rate': discount_rate,
        'terminal_growth_rate': terminal_growth_rate,
        'years': years
    }
    return _analyze_company_raw(ticker, company_name, assumptions)
```

Why two layers?
- Internal helpers (`_analyze_company_raw`) keep implementation details private.
- Public API functions (`add`, `analyze_one`) are deliberately small for controlled exposure via `allowed_functions`.

---
## 2. Analyst: Publish Model
Use the Publish panel or call the REST endpoint.

Minimum JSON body (POST `/api/publish_model`):
```json
{
  "name": "stock_intrinsic_v1",
  "code": "<paste the full code above>",
  "allowed_functions": ["add", "analyze_one"],
  "readme_md": "Initial intrinsic value model with add() and analyze_one().",
  "visibility": "public"
}
```
Response contains `model.id` (save it).

If using UI: ensure after first publish you update (or republish) so that `allowed_functions` includes both functions; otherwise investors cannot run them.

---
## 3. Investor: Discover & Request Edit
1. Navigate to `/published` (public catalog) and locate `stock_intrinsic_v1`.
2. Open details (network call: `GET /api/published_models?search=stock_intrinsic_v1`).
3. (Optional) Run allowed functions if permitted later (after they are set):
   - POST `/api/published_models/<id>/run` with:
     ```json
     {"function": "add", "args": [2,3] }
     ```
4. Request edit access (add future tickers, extend wrappers):
   - POST `/api/published_models/<id>/request_edit`:
     ```json
     {"reason": "Need to enhance function: add new stocks."}
     ```
   - Success returns `{ "ok": true, "request_id": "..." }`.

---
## 4. Analyst: Approve Edit Request
In `/vs_terminal` AUTHOR MGMT panel (auto-refresh) or via API:
- GET `/api/published_models/<id>/requests` (must be author) → shows `pending` entry.
- Approve (endpoint already implemented in app; assuming POST `/api/published_models/<id>/requests/<rid>/approve`).
- After approval, investor becomes an editor (authorized for updates & runs on restricted models).

---
## 5. Investor: Update Model (After Approval)
Use POST `/api/published_models/<id>/update` to extend allowed functions or README.
Example to add a new wrapper (first modify local code then submit updated full code OR append new function):
```json
{
  "readme_md": "Added broader multi-ticker support.",
  "allowed_functions": ["add", "analyze_one"],
  "code": "<re-upload full modified code with new functions>"
}
```
Server responds with `changed` map indicating which fields updated.

---
## 6. Running Public Functions (Investor or Analyst)
POST `/api/published_models/<id>/run` with examples:
1. Add: `{ "function": "add", "args": [7,5] }`
2. Analyze one ticker:
```json
{
  "function": "analyze_one",
  "args": ["TCS.NS", 40000, 0.08, 0.10, 0.04, 5, "Tata Consultancy Services"]
}
```
If function not in `allowed_functions`, response: `{ "error": "function not allowed" }`.

---
## 7. Extending: Adding New Public Analysis Function
Editors can introduce e.g. `analyze_pair(t1, t2, ...)` then update:
1. Modify code locally to add `def analyze_pair(...):` returning a combined dict.
2. POST update with `allowed_functions` including the new function.
3. Investor re-runs catalog → new function available via run endpoint.

---
## 8. Quick Endpoint Reference
| Purpose | Method & Path |
|---------|---------------|
| Publish model | POST `/api/publish_model` |
| List models | GET `/api/published_models` |
| Get model | GET `/api/published_models/<id>` |
| Run allowed function | POST `/api/published_models/<id>/run` |
| Request edit | POST `/api/published_models/<id>/request_edit` |
| List edit requests (author) | GET `/api/published_models/<id>/requests` |
| Approve/Deny request | POST `/api/published_models/<id>/requests/<rid>/approve` / `/deny` |
| Update model | POST `/api/published_models/<id>/update` |

---
## 9. Validation Scenario (Abbreviated)
1. Analyst publishes with `add` + `analyze_one` allowed.
2. Investor requests edit (reason: enhance function / add stocks).
3. Analyst approves; request disappears from AUTHOR MGMT.
4. Investor updates code & allowed functions (if needed) and runs new function.
5. Run count increments on successful executions.

---
## 10. Troubleshooting
| Symptom | Check |
|---------|-------|
| `function not allowed` | Ensure function name in `allowed_functions` for latest version. |
| Request not visible | Confirm same author user key; refresh panel. |
| Update unauthorized | Approval may still be pending; re-check requests list. |
| yfinance errors | Network / symbol mismatch; try different ticker or handle exception. |

---
## 11. Security Notes
- Keep public wrapper functions narrow; avoid exposing broad file or network I/O directly.
- Validate tickers / inputs server-side if expanding surface.

---
## 12. Next Enhancements (Optional)
- Auto-introspect functions and present a multi-select for `allowed_functions` at publish time.
- Add cached pricing to reduce repeated `yfinance` calls.
- Provide multi-ticker batch analysis with rate limit safeguards.

---
Document complete.
