# Plan Access Control Testing

## Summary
Updated `plan_access.py` to use your existing investor plan structure:

### Plan Hierarchy
- **retail** (level 0): Basic tier
- **pro** (level 1): Professional tier  
- **pro_plus** (level 2): Premium tier

### Dashboard Feature Limits (per day)

| Feature | Retail | Pro | Pro+ |
|---------|--------|-----|------|
| AI Chart Explain | 10 | 100 | 500 |
| Events Predictions | 50 | 500 | 2000 |
| AI General Chat | 25 | 200 | 1000 |
| Portfolio Insights | 5 | 50 | 200 |
| Model Subscriptions | 3 | 10 | Unlimited |

### Plan-Gated Features
- **Advanced Events Dashboard**: Requires Pro+
- **Bulk AI Reports**: Requires Pro+
- **Realtime Streams**: Requires Pro+
- **Model Recommendations**: Requires Pro+
- **Unlimited Subscriptions**: Requires Pro+

### Applied Enforcement
✅ `/api/ai/chart_explain` - Limited by `ai_chart_explain` quota
✅ `/api/events/predictions` - Limited by `events_predictions` quota

### Usage Headers
All protected endpoints return:
```
X-Feature-Usage: feature_name:used_count/limit
```

### Integration
The system reads investor plan from:
1. `session['investor_plan']` or `session['plan']`
2. `InvestorAccount.plan` column (fallback)
3. Defaults to 'retail' if none found

## Next Steps
To test in your dashboard:
1. Set `session['investor_plan'] = 'pro'` during investor login
2. Monitor X-Feature-Usage headers in browser dev tools
3. Endpoints will return 429 status when limits exceeded
4. Endpoints will return 403 when plan upgrade required

Ready for production with database persistence if needed.
