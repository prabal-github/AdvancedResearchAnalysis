# API Key & Secret Management Strategy

## Goals
- Remove hardcoded secrets from codebase.
- Centralize loading via environment variables / secure store.
- Support rotation with minimal downtime.

## Current Keys
| Purpose | Env Var | Notes |
|---------|---------|-------|
| Anthropic Claude | ANTHROPIC_API_KEY or CLAUDE_API_KEY | Used by ClaudeClient wrapper. |
| Fyers API | FYERS_CLIENT_ID | Public-ish identifier. |
| Fyers Access Token | FYERS_ACCESS_TOKEN | Short-lived; needs refresh. |

## Immediate Actions Implemented
1. All usage already reads from `os.getenv`. No literals added in new code.
2. Added structured prompt for AI insights (no secret exposure in logs).
3. Fyers helper caches instantiated client; does not log token.

## Recommended Enhancements
1. Add `.env` template (example) – do NOT commit real values.
2. Build `/admin/keys/status` endpoint (restricted) to view which providers are configured (no actual values returned).
3. Implement in-memory hot reload endpoint: POST `/admin/keys/reload` to re-read environment after rotation.
4. Optional: store encrypted copy (Fernet) of temporary session tokens in DB if refresh workflow added.

## Rotation Procedure (Anthropic)
1. Obtain new key from Anthropic console.
2. Set new key in hosting environment variable (e.g., AWS SSM Parameter Store or Secrets Manager) as `ANTHROPIC_API_KEY_NEW`.
3. Deploy a short management script to:
   - Inject `ANTHROPIC_API_KEY` with new value.
   - Hit `/admin/keys/reload` (to be implemented) or restart gunicorn workers.
4. After validation, delete old key from provider portal.

## Rotation Procedure (Fyers)
1. Generate new access token using OAuth / refresh flow.
2. Update `FYERS_ACCESS_TOKEN` env variable.
3. Trigger hot reload or restart.
4. Monitor quote endpoint logs for warnings.

## Hot Reload Sample (Pseudo-code)
```python
@app.route('/admin/keys/reload', methods=['POST'])
@admin_required
def reload_keys():
    app.config['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
    app.config['FYERS_ACCESS_TOKEN'] = os.getenv('FYERS_ACCESS_TOKEN')
    _reset_ai_and_fyers_clients()  # function to clear caches
    return jsonify({'ok': True})
```

## Logging Policies
- Never log full keys.
- At most log last 4 chars for troubleshooting (e.g., `...ABCD`).
- Suppress stack traces that could accidentally include headers.

## Monitoring
- Add counters: failed AI calls, failed Fyers quote calls (could indicate expired token).
- Alert after N consecutive failures.

## Future Hardening
- Integrate AWS Secrets Manager (boto3) lazy fetch with TTL cache.
- Implement automatic Fyers token refresh job.
- Provide UI for admin-triggered rotation events.

---
Generated guidance file; implement endpoints & cache reset helpers next if required.
