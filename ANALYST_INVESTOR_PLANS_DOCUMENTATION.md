# Analyst & Investor Plans Guide

This document explains the plan tiers, limits, upgrade workflows, and UI integration for:
- Analyst workspace (`/vs_terminal`)
- Investor published models catalog (`/published`)

---
## 1. Plan Tiers Overview

### Investor Plans
| Plan | Max Active Subscriptions | Per-Model Daily Run Limit | Notes |
|------|--------------------------|----------------------------|-------|
| retail (free) | 3 | 10 | Basic access; cannot exceed 10 runs per published model per day |
| pro | 10 | 10 | Higher subscription cap |
| pro_plus | Unlimited | Unlimited | No run throttling |

### Analyst Plans
| Plan | Publish Limit | Runs / Day (internal tools & model runs) | LLM Prompts / Day | LLM Tokens / Day | Full Analysis Mode | Provider Key Management |
|------|---------------|-------------------------------------------|------------------|------------------|--------------------|-------------------------|
| small (free) | 0 (disabled) | 20 | 10 | 20,000 | No | No |
| pro | 5 active published models | 100 | 100 | 200,000 | Partial (standard only) | No |
| pro_plus | Unlimited | Unlimited | Unlimited | Unlimited | Yes | Yes |

Notes:
- "Publish Limit" counts currently active (not unpublished) analyst-owned published models.
- "Runs / Day" / "LLM Prompts / Day" / "LLM Tokens / Day" reset daily (date-based rollover).
- Unlimited is represented internal as `None` limit.

---
## 2. Key Backend Endpoints

### Investor
- `GET /api/investor/plan_status` – Returns current investor plan, subscription usage, and remaining run info.
- Subscription enforcement in: `POST /api/subscribe_model` (caps based on plan).
- Per-model daily run gating in: `POST /api/published_models/<id>/run` (10 per day unless `pro_plus`).

### Analyst
- `GET /api/analyst/plan_status` – Returns usage counters & limits.
- `POST /api/analyst/upgrade/create_order` – Creates Razorpay order for `plan` (`pro` or `pro_plus`).
- `POST /api/analyst/upgrade/confirm` – Verifies Razorpay signature & activates plan (30‑day term).
- `POST /api/publish_model` – Enforces publish gating (rejects with 403 if over limit or plan disallows).
- `POST /api/published_models/<id>/run` – Increments analyst daily run counters.

### Admin Payment Settings
- `GET /api/admin/payment_settings` – Returns masked payment configuration.
- `POST /api/admin/payment_settings` – Upserts Razorpay keys, webhook secret, currency, and price points.

### Razorpay Configuration Persistence
- Stored in `payment_setting` table (single-row model) with fields: key_id, key_secret, webhook_secret, currency, price_*.
- Fallback: environment variables / `config.py` defaults if table unset.

---
## 3. Data Model Additions

`AnalystProfile` new columns:
- plan_expires_at (datetime)
- daily_llm_prompt_count (int)
- daily_llm_token_count (int)
- daily_run_count (int)

Daily counters reset when accessed if the stored `daily_usage_date` != today.

---
## 4. Frontend Integration

### /vs_terminal (Analyst Workspace)
New UI components:
1. Plan Button (activity bar, icon: layer-group) – Opens Plan Panel.
2. Plan Panel – Displays:
   - Current plan name & badge
   - Usage metrics (runs, prompts, tokens, publish limit) highlighting exceeded quotas
   - Upgrade buttons (Pro / Pro Plus) if user not already on that plan
   - Auto-launches Razorpay Checkout for selected upgrade plan
3. Upgrade Flow:
   - Click upgrade ⇒ `POST /api/analyst/upgrade/create_order`
   - Razorpay Checkout pops up (Checkout.js)
   - On success handler ⇒ `POST /api/analyst/upgrade/confirm`
   - Panel refreshes with updated limits
4. Publish Gating UX:
   - If publish attempt fails with plan error (`Publish limit reached` or `Publishing not included`), Plan Panel auto-opens with contextual prompt.

Admin-only enhancements:
- Activity bar credit-card button opens Payment Settings panel (flyout) for setting Key ID / Key Secret / Webhook Secret / prices.
- Secrets masked (only last 4 chars displayed) when loaded.

### /published (Investor Catalog)
Investor plan gating is server-side; UI can optionally query `GET /api/investor/plan_status` to show:
- Current plan & subscription count vs cap
- Per-model daily run remaining (not yet surfaced – implementable via response enhancement)
- Upgrade CTA (future extension; not yet implemented in UI).

---
## 5. Example JSON Responses

Analyst plan status (`GET /api/analyst/plan_status`):
```json
{
  "ok": true,
  "plan_info": {
    "plan": "pro",
    "publish_limit": 5,
    "runs_per_day": 100,
    "llm_prompts_per_day": 100,
    "llm_tokens_per_day": 200000,
    "allow_full_analysis": false,
    "provider_manage": false,
    "daily_llm_prompt_count": 7,
    "daily_llm_token_count": 18340,
    "daily_run_count": 12,
    "expires_at": "2025-09-16T10:14:02Z"
  }
}
```

Investor plan status (`GET /api/investor/plan_status`) (structure may include additional fields already present in code):
```json
{
  "ok": true,
  "plan": "retail",
  "subscription_cap": 3,
  "active_subscriptions": 2,
  "remaining_subscriptions": 1
}
```

Publish attempt blocked (analyst small plan):
```json
{
  "ok": false,
  "error": "Publishing not included in your plan",
  "plan_status": {"plan":"small", "publish_limit":0, ...}
}
```

---
## 6. Upgrade Flow Sequence (Analyst)
1. User clicks Upgrade (Pro / Pro Plus) in Plan Panel.
2. JS: `POST /api/analyst/upgrade/create_order` with `{plan}`.
3. Backend: Creates Razorpay order using configured credentials; returns `order`, `public_key`, `amount`, `currency`.
4. Frontend: Launches Checkout.js widget.
5. After payment success, Checkout handler posts to `/api/analyst/upgrade/confirm` with `{plan, order_id, payment_id, signature}`.
6. Backend: Verifies signature, updates `AnalystProfile.plan` + `plan_expires_at` (+30 days), returns success JSON.
7. UI refreshes plan status.

---
## 7. Error Handling Patterns
| Scenario | Response Code | JSON Pattern | UI Behavior |
|----------|---------------|--------------|-------------|
| Publish blocked | 403 | `{ok:false,error:...,plan_status:...}` | Auto-open Plan Panel w/ prompt |
| Run limit exceeded (investor) | 429 | `{ok:false,error:"Daily run limit reached..."}` | Show status; optional prompt to upgrade (future) |
| Analyst run/quota exceeded | 429 | `{ok:false,error:"Daily LLM prompt limit reached",plan_status:...}` | Plan Panel can be opened manually |
| Payment settings missing | 500 (create_order) | `{ok:false,error:"Razorpay not configured"}` | Admin must configure keys |
| Signature invalid | 400 | `{ok:false,error:"Signature verify failed: ..."}` | Show verification error |

---
## 8. Security & Best Practices
- Razorpay secrets are only editable by admin (server-side enforced via `_require_admin`).
- Client never sees raw key_secret or webhook_secret; masked in GET response.
- Signature verification required before activating plan.
- Daily counters persisted; rely on server authoritative gating (never trust only the UI).
- Plan gating consistently performed server-side before: publish, run, and LLM usage (prompt counts/tokens).

---
## 9. Future Enhancements (Suggested)
- Investor UI upgrade panel mirroring analyst panel.
- Webhook endpoint to auto-handle payment events & renewals (e.g., `/api/payments/webhook`).
- Grace period logic when plan expires.
- Email notifications for quota nearing or plan expiry.
- Token usage visualization graphs.
- Bulk publish limit increment for high-performing analysts (admin override).

---
## 10. Quick Testing Steps
1. Start app and login as admin; open `/vs_terminal`.
2. Use credit-card icon → set Razorpay test keys.
3. Open layer-group icon → note current analyst plan (likely `small`).
4. Attempt to publish code (should be blocked on `small`).
5. Click Upgrade to Pro; complete Razorpay test payment; confirm plan panel updates.
6. Publish again (should succeed until limit reached).
7. Upgrade to Pro Plus; publish unlimited; observe no further gating.
8. As investor account: subscribe to models until limit reached; attempt extra subscription to receive error.

---
## 11. Key Code Reference
- Gating helpers: `_analyst_publish_allowed`, `_analyst_register_run`, `_analyst_plan_info` in `app.py`.
- Endpoints: `/api/analyst/plan_status`, `/api/analyst/upgrade/create_order`, `/api/analyst/upgrade/confirm`, `/api/admin/payment_settings`.
- UI logic: `templates/vs_terminal.html` (Plan Panel & Payment Settings panel).

---
**Document Version:** 2025-08-17
