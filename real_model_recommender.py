"""Real ML model recommendation logic based on live events/news feed.
Designed to work without heavy ML deps; will enhance if scikit-learn available.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Iterable
import re
import hashlib, json, time
from threading import RLock

@dataclass
class ModelDescriptor:
    model: str
    category: str  # alpha|risk|hedge|macro
    alpha_potential: str  # low|moderate|high
    risk_mitigation: str  # low|moderate|high|n/a
    expected_alpha_range: str
    lookback_window: str
    retrain_frequency: str
    features: List[str]
    why: str

BASE_MODELS: List[ModelDescriptor] = [
    ModelDescriptor("Macro Inflation Nowcast Model","macro","moderate","low","0.5-1.2%","12M","Monthly",["CPI","PPI","FX","Commodities"],"Inflation / CPI signals present"),
    ModelDescriptor("Policy Rate Decision Impact Model","macro","moderate","moderate","0.4-1.0%","18M","Per-Meeting",["Rates Futures","Yield Curve","Swap Spreads"],"Central bank / policy wording detected"),
    ModelDescriptor("Volatility Regime Classifier","risk","low","high","0.2-0.5% (cost saving)","6M","Weekly",["VIX","Realized Vol","Skew","Volume"],"Elevated volatility context"),
    ModelDescriptor("Options Skew Arbitrage Model","alpha","high","moderate","1.0-2.5%","3M","Daily",["IV Skew","Term Structure","Gamma Exposure"],"Volatility + event clustering suggests skew dislocations"),
    ModelDescriptor("Earnings Surprise Gradient Booster","alpha","moderate","low","0.8-1.8%","8Q","Quarterly",["Revision Momentum","Sentiment","Accruals"],"Earnings / results related headlines"),
    ModelDescriptor("Commodity Shock Spillover Model","risk","moderate","high","0.3-0.7%","24M","Monthly",["Oil","Gas","FX","Freight"],"Energy / commodity shock terms appear"),
    ModelDescriptor("Labor Market Momentum Model","macro","moderate","moderate","0.4-0.9%","18M","Monthly",["Claims","Payrolls","Wages"],"Employment / labor indicators referenced"),
    ModelDescriptor("Growth Cycle Phase Classifier","macro","moderate","moderate","0.5-1.0%","36M","Quarterly",["GDP","PMI","Credit Spreads"],"Growth / GDP cycle references"),
]

KEYWORD_MAP = {
    r"\b(cpi|inflation|prices?)\b": "Macro Inflation Nowcast Model",
    r"\b(fed|fomc|rbi|policy rate|central bank)\b": "Policy Rate Decision Impact Model",
    r"\b(earnings|results|quarterly|q[1-4])\b": "Earnings Surprise Gradient Booster",
    r"\b(oil|brent|crude|energy)\b": "Commodity Shock Spillover Model",
    r"\b(jobless|employment|unemployment|payrolls|claims)\b": "Labor Market Momentum Model",
    r"\b(gdp|growth|pmi)\b": "Growth Cycle Phase Classifier",
    r"\b(volatility|vix|fear index)\b": "Volatility Regime Classifier",
}

def _model_versions() -> Dict[str, Dict[str, Any]]:
    """Return lightweight version info for each base model.
    Version hash = sha1 of model name + feature list + retrain_frequency.
    """
    versions = {}
    for m in BASE_MODELS:
        payload = f"{m.model}|{','.join(m.features)}|{m.retrain_frequency}"
        h = hashlib.sha1(payload.encode('utf-8')).hexdigest()[:10]
        versions[m.model] = {
            'version': h,
            'generated_at': int(time.time()),
            'features': m.features,
            'retrain_frequency': m.retrain_frequency,
            'category': m.category,
        }
    return versions

# Reverse mapping model -> patterns (list)
MODEL_PATTERNS: Dict[str, list[str]] = {}
for pattern, model_name in KEYWORD_MAP.items():
    MODEL_PATTERNS.setdefault(model_name, []).append(pattern)
# Add additional patterns for models not directly keyed
MODEL_PATTERNS.setdefault('Options Skew Arbitrage Model', []).extend([r"\b(skew|gamma|options?)\b"])

def _fuzzy_ratio(a: str, b: str) -> float:
    try:
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    except Exception:
        return 0.0

_MODEL_MATCH_CACHE: Dict[str, Any] = {'ttl': 300, 'data': {}, 'lock': RLock()}  # key -> (ts, results)

def _cache_key(text: str, vix_level: float | None) -> str:
    hv = hashlib.sha1((text.lower() + '|' + str(int((vix_level or 0)//5))).encode('utf-8')).hexdigest()
    return hv

def match_models_for_text(text: str, vix_level: float | None = None, top_k: int = 5, min_score: float = 0.0) -> List[Dict[str, Any]]:
    """Return ranked model matches for a given text with scores and reasons.

    Caches results for identical (text,vix bucket) for TTL seconds to improve performance.
    Filters out matches with score < min_score (after scoring) while keeping ranking.
    """
    if not text:
        return []
    key = _cache_key(text, vix_level)
    now_ts = time.time()
    ttl = _MODEL_MATCH_CACHE['ttl']
    try:
        with _MODEL_MATCH_CACHE['lock']:
            cached = _MODEL_MATCH_CACHE['data'].get(key)
            if cached and (now_ts - cached[0] < ttl):
                # Apply min_score filtering on cached full results
                filtered = [m for m in cached[1] if m['score'] >= min_score]
                return filtered[:top_k]
    except Exception:
        pass

    text_l = text.lower()
    results = []
    for md in BASE_MODELS:
        score = 0.0
        reasons = []
        for pat in MODEL_PATTERNS.get(md.model, []):
            try:
                if re.search(pat, text_l):
                    score += 1.0
                    reasons.append(f"pattern:{pat}")
            except Exception:
                pass
        sim = _fuzzy_ratio(text_l[:500], (md.why or '').lower())
        if sim > 0.5:
            score += sim * 0.5
            reasons.append(f"why_sim:{sim:.2f}")
        if md.model in ('Volatility Regime Classifier','Options Skew Arbitrage Model') and vix_level and vix_level > VOL_ELEVATED_THRESHOLD:
            score += 0.3
            reasons.append(f"vix:{vix_level:.1f}")
        if score > 0:
            results.append({'model': md.model, 'score': round(score,3), 'reasons': reasons})
    results.sort(key=lambda x: x['score'], reverse=True)
    # store full (unfiltered) results in cache
    try:
        with _MODEL_MATCH_CACHE['lock']:
            _MODEL_MATCH_CACHE['data'][key] = (now_ts, results)
    except Exception:
        pass
    # apply min score filter
    if min_score > 0:
        results = [r for r in results if r['score'] >= min_score]
    return results[:top_k]

def match_models_batch(items: List[Dict[str, Any]], vix_level: float | None = None) -> Dict[str, Any]:
    """Batch matching: items = [{'id':..., 'text':...}, ...] returns dict id -> matches list"""
    out: Dict[str, Any] = {}
    for it in items or []:
        pid = str(it.get('id') or it.get('event_id') or it.get('idx') or len(out))
        out[pid] = match_models_for_text(it.get('text',''), vix_level=vix_level)
    return out

VOL_ELEVATED_THRESHOLD = 20
VOL_HIGH_THRESHOLD = 30

try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # optional
    _HAS_SK = True
except Exception:
    _HAS_SK = False


def _collect_text(items: Iterable[Dict[str, Any]]) -> str:
    parts = []
    for it in items:
        for k in ('title','summary','description'):
            v = it.get(k)
            if v:
                parts.append(str(v))
    return ' '.join(parts).lower()


def recommend_models(events: List[Dict[str, Any]], predictions: List[Dict[str, Any]], vix_level: float | None) -> List[Dict[str, Any]]:
    text_blob = _collect_text(events) + ' ' + _collect_text(predictions)
    selected = {}

    # Keyword rules
    for pattern, model_name in KEYWORD_MAP.items():
        if re.search(pattern, text_blob):
            md = next((m for m in BASE_MODELS if m.model == model_name), None)
            if md:
                selected[md.model] = md

    # Volatility driven models
    if vix_level is not None:
        if vix_level > VOL_ELEVATED_THRESHOLD:
            md = next((m for m in BASE_MODELS if m.model == "Volatility Regime Classifier"), None)
            if md:
                selected[md.model] = md
        if vix_level > VOL_HIGH_THRESHOLD:
            # Add skew arbitrage if not present
            md = next((m for m in BASE_MODELS if m.model == "Options Skew Arbitrage Model"), None)
            if md:
                selected[md.model] = md

    # Prediction diversity rule
    if len(predictions) >= 2:
        md = next((m for m in BASE_MODELS if m.model == "Growth Cycle Phase Classifier"), None)
        if md:
            selected.setdefault(md.model, md)

    models = list(selected.values())

    # Optional TF-IDF weighting to prioritize relevance if sklearn available
    if _HAS_SK and models:
        try:
            corpus = [text_blob] + [m.why.lower() + ' ' + m.model.lower() for m in models]
            vec = TfidfVectorizer(max_features=200, stop_words='english')
            X = vec.fit_transform(corpus)
            relevance = (X[0] @ X[1:].T).toarray().flatten()
            ranked = sorted(zip(models, relevance), key=lambda x: x[1], reverse=True)
            models = [m for m,_ in ranked]
        except Exception:
            pass

    return [asdict(m) for m in models]


def get_model_catalog(events: List[Dict[str, Any]], predictions: List[Dict[str, Any]], vix_level: float | None) -> List[Dict[str, Any]]:
    """Return full catalog with triggered flags so UI can always show all models.

    Adds fields:
      triggered: bool
      trigger_reason: str (why it triggered now)
    """
    # First reuse selection logic
    selected = {m['model']: m for m in recommend_models(events, predictions, vix_level)}

    catalog: List[Dict[str, Any]] = []
    text_blob = _collect_text(events) + ' ' + _collect_text(predictions)
    lower_blob = text_blob.lower()

    # Additional volatility info
    vol_context = None
    try:
        if vix_level is not None:
            if vix_level > VOL_HIGH_THRESHOLD:
                vol_context = f"VIX very high ({vix_level:.1f})"
            elif vix_level > VOL_ELEVATED_THRESHOLD:
                vol_context = f"VIX elevated ({vix_level:.1f})"
    except Exception:
        pass

    for md in BASE_MODELS:
        d = asdict(md)
        trig = md.model in selected
        reason = ''
        if trig:
            # Use existing why field if selected
            reason = d.get('why') or 'Signal match'
        else:
            # Check if close to triggering (e.g., volatility context for vol models)
            if md.model == 'Volatility Regime Classifier' and vol_context:
                reason = vol_context
        d['triggered'] = trig
        d['trigger_reason'] = reason
        catalog.append(d)
    return catalog
