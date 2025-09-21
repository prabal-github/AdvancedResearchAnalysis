"""Plan-based feature access control matching existing hourly/daily quota system.
Uses the established investor plan structure from USAGE_AND_PLANS.md.
Replace in-memory counters with Redis/DB in production.
"""
from datetime import datetime
from collections import defaultdict
from flask import session, jsonify

PLAN_LEVELS = {"retail":0,"pro":1,"pro_plus":2}

# Hourly quotas per plan (from USAGE_AND_PLANS.md)
HOURLY_QUOTAS = {
    "retail": 120,     # 120/hour
    "pro": 1200,       # 1200/hour  
    "pro_plus": 5000   # 5000/hour
}

# Daily caps for entry tiers
DAILY_CAPS = {
    "retail": 300,     # 300/day for retail
    "pro": 3600,       # 1200*3 (rough daily estimate)
    "pro_plus": 15000  # 5000*3 (rough daily estimate)
}

# Feature-specific daily limits (in addition to overall quotas)
FEATURE_LIMITS = {
    "ai_chart_explain": {"retail":10, "pro":100, "pro_plus":500},
    "events_predictions": {"retail":50, "pro":500, "pro_plus":2000},
    "ai_general_chat": {"retail":25, "pro":200, "pro_plus":1000},
    "portfolio_insights": {"retail":5, "pro":50, "pro_plus":200},
    "model_subscriptions": {"retail":3, "pro":10, "pro_plus":999999}  # Unlimited for pro_plus
}

# Feature availability gating by minimum plan level
FEATURE_MIN_PLAN = {
    "advanced_events_dashboard": "pro",
    "bulk_ai_reports": "pro", 
    "realtime_streams": "pro_plus",
    "model_recommendations": "pro",
    "unlimited_subscriptions": "pro_plus"
}

# In-memory counters: {date_hour: {investor_id: count}}, {date: {investor_id: {feature: count}}}
_hourly_counters = defaultdict(lambda: defaultdict(int))
_daily_counters = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))


def _current_date_key():
    return datetime.now().strftime('%Y-%m-%d')

def _current_hour_key():
    return datetime.now().strftime('%Y-%m-%d %H')

def get_current_usage(investor_id, plan):
    """Get current hourly and daily usage for an investor."""
    hour_key = _current_hour_key()
    day_key = _current_date_key()
    
    # Get hourly usage across all requests
    hourly_usage = _hourly_counters[hour_key][investor_id]
    
    # Get daily usage across all features
    daily_usage = sum(_daily_counters[day_key][investor_id].values())
    
    # Get quotas for this plan
    hourly_quota = HOURLY_QUOTAS.get(plan, 0)
    daily_cap = DAILY_CAPS.get(plan, 0)
    
    return {
        "hourly_usage": hourly_usage,
        "hourly_quota": hourly_quota,
        "hourly_remaining": max(0, hourly_quota - hourly_usage),
        "daily_usage": daily_usage,
        "daily_cap": daily_cap,
        "daily_remaining": max(0, daily_cap - daily_usage),
        "hour_key": hour_key,
        "day_key": day_key
    }

def check_quota_availability(investor_id, plan, feature=None):
    """Check if investor has quota available (hourly and daily limits)."""
    usage = get_current_usage(investor_id, plan)
    
    # Check hourly quota first
    if usage["hourly_remaining"] <= 0:
        return False, f"Hourly quota exceeded ({usage['hourly_usage']}/{usage['hourly_quota']})"
    
    # Check daily cap
    if usage["daily_remaining"] <= 0:
        return False, f"Daily cap exceeded ({usage['daily_usage']}/{usage['daily_cap']})"
    
    # Check feature-specific daily limit if specified
    if feature and feature in FEATURE_LIMITS:
        day_key = _current_date_key()
        feature_usage = _daily_counters[day_key][investor_id][feature]
        feature_limit = FEATURE_LIMITS[feature].get(plan, 0)
        
        if feature_usage >= feature_limit:
            return False, f"Daily {feature} limit exceeded ({feature_usage}/{feature_limit})"
    
    return True, "Quota available"

def _increment_usage(investor_id, feature, cost=1):
    """Increment both hourly and daily usage counters."""
    hour_key = _current_hour_key()
    day_key = _current_date_key()
    
    # Increment hourly counter
    _hourly_counters[hour_key][investor_id] += cost
    
    # Increment feature-specific daily counter
    if feature:
        _daily_counters[day_key][investor_id][feature] += cost
    
    return _daily_counters[day_key][investor_id][feature]


def get_investor_plan(default="retail"):
    """Get investor plan from session or database."""
    # Try session first
    plan = session.get('investor_plan') or session.get('plan')
    if plan: return plan.lower()
    
    # Attempt lazy model lookup if available
    investor_id = session.get('investor_id') or session.get('user_id')
    if not investor_id:
        return default
    
    try:
        from investor_terminal_export.models import InvestorAccount  # type: ignore
        acct = InvestorAccount.query.filter_by(id=investor_id).first()
        if acct and getattr(acct, 'plan', None):
            return str(acct.plan).lower()
    except Exception:
        pass
    return default


def has_min_plan(required_plan: str) -> bool:
    """Check if user's plan meets minimum requirement."""
    user_plan = get_investor_plan()
    return PLAN_LEVELS.get(user_plan,0) >= PLAN_LEVELS.get(required_plan,0)


def _get_usage(investor_id, feature):
    day = _current_date_key()
    return _daily_counters[day][investor_id][feature]


def enforce_feature(feature_name):
    """Decorator enforcing hourly quotas, daily caps, and feature limits."""
    from functools import wraps
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            investor_id = session.get('investor_id') or session.get('user_id') or 'anon'
            plan = get_investor_plan()
            
            # Check hourly and daily quotas first
            quota_ok, quota_msg = check_quota_availability(investor_id, plan, feature_name)
            if not quota_ok:
                return jsonify({
                    'error': 'quota_exceeded',
                    'message': quota_msg,
                    'feature': feature_name,
                    'plan': plan
                }), 429
            
            # Minimum plan gate
            min_plan = FEATURE_MIN_PLAN.get(feature_name)
            if min_plan and not has_min_plan(min_plan):
                return jsonify({
                    'error':'plan_upgrade_required',
                    'feature': feature_name,
                    'required_plan': min_plan,
                    'current_plan': plan
                }), 403
            
            # Feature-specific daily limit gate
            limits = FEATURE_LIMITS.get(feature_name)
            if limits:
                limit = limits.get(plan, limits.get('retail', 0))
                used = _get_usage(investor_id, feature_name)
                if limit > 0 and used >= limit:
                    return jsonify({
                        'error':'daily_limit_reached',
                        'feature': feature_name,
                        'plan': plan,
                        'limit': limit,
                        'used': used
                    }), 429
                
                # Increment usage counters (both hourly and daily)
                new_used = _increment_usage(investor_id, feature_name)
                
                # Attach usage headers via response object after execution
                resp = fn(*args, **kwargs)
                try:
                    # If response is a tuple (resp, status), handle first element
                    if isinstance(resp, tuple):
                        flask_resp = resp[0]
                        status = resp[1]
                    else:
                        flask_resp = resp
                        status = None
                    hdr_target = flask_resp
                    
                    # Add comprehensive usage headers
                    usage_info = get_current_usage(investor_id, plan)
                    hdr_target.headers['X-Feature-Usage'] = f"{feature_name}:{new_used}/{limit}"
                    hdr_target.headers['X-Hourly-Usage'] = f"{usage_info['hourly_usage']}/{usage_info['hourly_quota']}"
                    hdr_target.headers['X-Daily-Usage'] = f"{usage_info['daily_usage']}/{usage_info['daily_cap']}"
                    
                    if status:
                        return flask_resp, status
                    return flask_resp
                except Exception:
                    return resp
            else:
                # No feature limits, just increment hourly usage
                _increment_usage(investor_id, feature_name)
                
            return fn(*args, **kwargs)
        return wrapper
    return decorator

__all__ = [
    'enforce_feature','get_investor_plan','has_min_plan','get_current_usage','check_quota_availability',
    'PLAN_LEVELS','FEATURE_LIMITS','FEATURE_MIN_PLAN','HOURLY_QUOTAS','DAILY_CAPS'
]
