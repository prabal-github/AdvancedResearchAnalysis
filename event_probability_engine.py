"""Event Probability Engine
Computes occurrence probabilities for upcoming events using current events list,
latest news items, and optional volatility context.

Designed as a lightweight, explainable heuristic scaffold that can later
be replaced or calibrated with a learned model (e.g., logistic regression / GBM).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import math
import re
import json
import os
from datetime import datetime, timezone

IMPACT_MAP = {
    'low': 1,
    'medium': 2,
    'high': 3,
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5
}

WORD_RE = re.compile(r"[A-Za-z]{3,}")

@dataclass
class ProbabilityFactor:
    name: str
    value: float
    weight: float
    contribution: float
    description: str

@dataclass
class EventProbabilityResult:
    event_id: str
    title: str
    scheduled_time: Optional[str]
    probability: float
    impact: int
    confidence: float
    factors: List[ProbabilityFactor] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_id': self.event_id,
            'title': self.title,
            'scheduled_time': self.scheduled_time,
            'probability': round(self.probability, 4),
            'confidence': round(self.confidence, 3),
            'predicted_impact': self.impact,
            'probability_factors': [
                {
                    'name': f.name,
                    'value': f.value,
                    'weight': f.weight,
                    'contribution': round(f.contribution, 4),
                    'description': f.description
                } for f in self.factors
            ]
        }

class EventProbabilityEngine:
    def __init__(self):
        # Default heuristic weights for transparent baseline
        self.heuristic_weights = {
            'base':  -1.2,
            'impact': 0.35,
            'news_support': 0.55,
            'volatility': 0.4,
            'time_decay': 0.9,
            'recency_inverse': 0.5,
            'news_sentiment': 0.2,
            'news_similarity': 0.25
        }
        self.model_weights_path = os.path.join('data', 'probability_model_weights.json')
        self.calibration_store_path = os.path.join('data', 'probability_calibration.json')
        self.model_weights = self._load_or_init_model_weights()
        self.last_trained_at = self.model_weights.get('updated_at')

    def compute_probabilities(self, event_items: List[Dict[str, Any]], news_items: List[Dict[str, Any]], vix_level: Optional[float] = None, max_events: int = 5) -> List[Dict[str, Any]]:
        # Optionally attempt retrain if enough labeled history
        self._maybe_retrain_from_history()
        # Filter to upcoming events (timestamp > now UTC)
        now = datetime.now(timezone.utc)
        upcoming_candidates = []
        for ev in event_items:
            ts_raw = ev.get('published_at') or ev.get('scheduled_time')
            if not ts_raw:
                continue
            dt = self._parse_time(ts_raw)
            if not dt:
                continue
            if dt <= now:
                continue
            upcoming_candidates.append((ev, dt))
        # Sort by soonest
        upcoming_candidates.sort(key=lambda x: x[1])
        results: List[EventProbabilityResult] = []
        # Pre-compute news keyword index (simple count of event title tokens in recent news)
        recent_news = [n for n in news_items if (self._parse_time(n.get('published_at')) or now) >= now.replace(hour=0, minute=0, second=0, microsecond=0)]
        news_text_blob = " \n".join([(n.get('title') or '') + ' ' + (n.get('summary') or '') for n in recent_news]).lower()

        for ev, dt in upcoming_candidates[:max_events]:
            impact_raw = ev.get('impact')
            if isinstance(impact_raw, str):
                impact_numeric = IMPACT_MAP.get(impact_raw.lower(), 2)
            else:
                impact_numeric = IMPACT_MAP.get(impact_raw, 2)

            hours_ahead = max(0.1, (dt - now).total_seconds() / 3600.0)

            # Feature: time decay (closer events -> higher weight)
            time_decay = math.exp(-hours_ahead / 24.0)  # 1 day characteristic decay

            # Feature: recent news support (keyword overlap count normalized)
            title = ev.get('title') or ''
            tokens = [t.lower() for t in WORD_RE.findall(title)][:6]
            news_support_raw = sum(news_text_blob.count(t) for t in tokens)
            news_support = min(5.0, news_support_raw / 2.0)  # scale down

            # Feature: volatility factor
            vol_factor = 0.0
            if vix_level is not None:
                if vix_level > 30:
                    vol_factor = 1.0
                elif vix_level > 20:
                    vol_factor = 0.6
                elif vix_level > 15:
                    vol_factor = 0.3
                else:
                    vol_factor = 0.1

            # Feature: recency inverse (if similar category seen very recently reduce probability of another unless recurrent type)
            recency_inverse = 1.0
            cat = (ev.get('category') or '').lower()
            last_time_same_cat = self._last_category_time(cat, event_items, now)
            if last_time_same_cat:
                hours_since_cat = (now - last_time_same_cat).total_seconds() / 3600.0
                recency_inverse = 1.0 / (1.0 + (hours_since_cat / 48.0))  # within 2 days lowers value

            # Additional Features: sentiment & similarity
            news_sentiment = self._aggregate_sentiment(recent_news, tokens)
            news_similarity = self._jaccard_similarity(title, news_text_blob)

            # Compute probability using either trained logistic weights or heuristic fallback
            if self.model_weights.get('trained', False):
                w = self.model_weights['weights']
            else:
                w = self.heuristic_weights

            logit = (
                w.get('base', -1.2) +
                w.get('impact', 0.0) * impact_numeric +
                w.get('news_support', 0.0) * news_support +
                w.get('volatility', 0.0) * vol_factor +
                w.get('time_decay', 0.0) * time_decay +
                w.get('recency_inverse', 0.0) * recency_inverse +
                w.get('news_sentiment', 0.0) * news_sentiment +
                w.get('news_similarity', 0.0) * news_similarity
            )
            probability = 1.0 / (1.0 + math.exp(-logit))
            probability = max(0.01, min(0.99, probability))

            # Confidence heuristic
            confidence = 0.5
            if news_support >= 2: confidence += 0.15
            if impact_numeric >= 3: confidence += 0.15
            if vol_factor >= 0.6: confidence += 0.1
            if self.model_weights.get('trained', False): confidence += 0.05  # slight boost for trained model
            confidence = min(0.95, confidence)

            factors = [
                ProbabilityFactor('impact', impact_numeric, w.get('impact',0), w.get('impact',0) * impact_numeric, 'Higher impact increases probability'),
                ProbabilityFactor('news_support', news_support, w.get('news_support',0), w.get('news_support',0) * news_support, 'Recent related news increases probability'),
                ProbabilityFactor('volatility', vol_factor, w.get('volatility',0), w.get('volatility',0) * vol_factor, 'Elevated volatility raises chances of materialization'),
                ProbabilityFactor('time_decay', time_decay, w.get('time_decay',0), w.get('time_decay',0) * time_decay, 'Near-term scheduled time increases probability'),
                ProbabilityFactor('recency_inverse', recency_inverse, w.get('recency_inverse',0), w.get('recency_inverse',0) * recency_inverse, 'Very recent similar event slightly reduces probability'),
                ProbabilityFactor('news_sentiment', news_sentiment, w.get('news_sentiment',0), w.get('news_sentiment',0)*news_sentiment, 'Aggregate sentiment relevance'),
                ProbabilityFactor('news_similarity', news_similarity, w.get('news_similarity',0), w.get('news_similarity',0)*news_similarity, 'Token similarity with recent news')
            ]

            results.append(EventProbabilityResult(
                event_id=ev.get('id') or '',
                title=title,
                scheduled_time=dt.isoformat(),
                probability=probability,
                confidence=confidence,
                impact=min(5, impact_numeric if impact_numeric <= 5 else 5),
                factors=factors
            ))

        output = [r.to_dict() for r in results]
        # Record predictions for future calibration
        for row in output:
            self._record_prediction(row)
        return output

    def _parse_time(self, ts: Optional[str]):
        if not ts:
            return None
        try:
            # Accept both naive and timezone aware
            if ts.endswith('Z'):
                ts = ts[:-1]
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return None

    def _last_category_time(self, category: str, events: List[Dict[str, Any]], now: datetime):
        if not category:
            return None
        last_dt = None
        for ev in events:
            cat = (ev.get('category') or '').lower()
            if cat != category:
                continue
            dt = self._parse_time(ev.get('published_at') or ev.get('scheduled_time'))
            if dt and dt <= now:
                if last_dt is None or dt > last_dt:
                    last_dt = dt
        return last_dt

    # --- Sentiment & Similarity Helpers ---
    def _aggregate_sentiment(self, news: List[Dict[str, Any]], tokens: List[str]) -> float:
        # Lightweight heuristic: sentiment proxy = (positive_hits - negative_hits)/len(tokens+1)
        if not tokens:
            return 0.0
        positives = {'gain','growth','positive','surge','beat','strong','improve'}
        negatives = {'loss','weak','decline','miss','fall','risk','concern','volatility'}
        text = ' '.join([(n.get('title') or '') + ' ' + (n.get('summary') or '') for n in news]).lower()
        pos = sum(text.count(p) for p in positives)
        neg = sum(text.count(n) for n in negatives)
        score = (pos - neg) / (len(tokens) + 1)
        return max(-2.0, min(2.0, score))  # clamp

    def _jaccard_similarity(self, title: str, corpus: str) -> float:
        tset = set(WORD_RE.findall(title.lower()))
        if not tset:
            return 0.0
        cset = set(WORD_RE.findall(corpus.lower()))
        if not cset:
            return 0.0
        inter = len(tset & cset)
        union = len(tset | cset)
        return inter / union if union else 0.0

    # --- Calibration Storage & Training ---
    def _record_prediction(self, row: Dict[str, Any]):
        try:
            os.makedirs(os.path.dirname(self.calibration_store_path), exist_ok=True)
            existing = []
            if os.path.isfile(self.calibration_store_path):
                with open(self.calibration_store_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            existing.append({
                'event_id': row['event_id'],
                'timestamp': datetime.utcnow().isoformat(),
                'probability': row['probability'],
                'confidence': row['confidence'],
                'outcome': None,  # to be filled when known
                'factors': row['probability_factors']
            })
            # keep last 5000
            if len(existing) > 5000:
                existing = existing[-5000:]
            with open(self.calibration_store_path, 'w', encoding='utf-8') as f:
                json.dump(existing, f)
        except Exception:
            pass

    def _load_or_init_model_weights(self) -> Dict[str, Any]:
        try:
            if os.path.isfile(self.model_weights_path):
                with open(self.model_weights_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {'trained': False, 'weights': self.heuristic_weights.copy(), 'updated_at': None}

    def _save_model_weights(self):
        try:
            os.makedirs(os.path.dirname(self.model_weights_path), exist_ok=True)
            self.model_weights['updated_at'] = datetime.utcnow().isoformat()
            with open(self.model_weights_path, 'w', encoding='utf-8') as f:
                json.dump(self.model_weights, f, indent=2)
        except Exception:
            pass

    def _maybe_retrain_from_history(self, min_records: int = 50):
        # Only retrain if there are enough labeled outcomes and not trained recently
        try:
            if not os.path.isfile(self.calibration_store_path):
                return
            with open(self.calibration_store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            labeled = [d for d in data if isinstance(d.get('outcome'), (int, float))]
            if len(labeled) < min_records:
                return
            # Avoid retraining more than once per hour
            if self.last_trained_at:
                try:
                    last_dt = datetime.fromisoformat(self.last_trained_at.replace('Z',''))
                    if (datetime.utcnow() - last_dt).total_seconds() < 3600:
                        return
                except Exception:
                    pass
            # Prepare feature matrix
            X = []
            y = []
            for row in labeled[-1000:]:  # use recent 1000
                factor_map = {f['name']: f['value'] for f in row.get('factors', [])}
                X.append([
                    factor_map.get('impact',0),
                    factor_map.get('news_support',0),
                    factor_map.get('volatility',0),
                    factor_map.get('time_decay',0),
                    factor_map.get('recency_inverse',0),
                    factor_map.get('news_sentiment',0),
                    factor_map.get('news_similarity',0)
                ])
                y.append(1 if row.get('outcome') else 0)
            # Simple gradient descent logistic regression
            weights = [0.0]*7
            bias = 0.0
            lr = 0.01
            epochs = 120
            n = len(X)
            if n < min_records:
                return
            for _ in range(epochs):
                grad_w = [0.0]*7
                grad_b = 0.0
                for xi, yi in zip(X,y):
                    z = bias + sum(w*a for w,a in zip(weights, xi))
                    p = 1.0/(1.0+math.exp(-z))
                    diff = p - yi
                    for j in range(7):
                        grad_w[j] += diff * xi[j]
                    grad_b += diff
                for j in range(7):
                    weights[j] -= lr * grad_w[j]/n
                bias -= lr * grad_b/n
            # Map weights back
            names = ['impact','news_support','volatility','time_decay','recency_inverse','news_sentiment','news_similarity']
            learned = {name: w for name, w in zip(names, weights)}
            learned['base'] = bias
            self.model_weights = {'trained': True, 'weights': learned}
            self.last_trained_at = datetime.utcnow().isoformat()
            self._save_model_weights()
        except Exception:
            pass

    def calibration_stats(self, bins: int = 10) -> Dict[str, Any]:
        try:
            if not os.path.isfile(self.calibration_store_path):
                return {'records': 0, 'bins': [], 'brier_score': None}
            with open(self.calibration_store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            labeled = [d for d in data if isinstance(d.get('outcome'), (int,float))]
            if not labeled:
                return {'records': len(data), 'bins': [], 'brier_score': None}
            brier_sum = 0.0
            bins_data: List[Tuple[float,float,int]] = []  # p_avg, o_avg, count
            for b in range(bins):
                low = b / bins
                high = (b+1)/bins
                subset = [d for d in labeled if low <= d['probability'] < high]
                if subset:
                    p_avg = sum(d['probability'] for d in subset)/len(subset)
                    o_avg = sum(d['outcome'] for d in subset)/len(subset)
                    bins_data.append((p_avg, o_avg, len(subset)))
            for d in labeled:
                brier_sum += (d['probability'] - d['outcome'])**2
            brier = brier_sum/len(labeled)
            return {
                'records': len(data),
                'labeled_records': len(labeled),
                'brier_score': round(brier,4),
                'bins': [
                    {'predicted_avg': round(p,4), 'observed_avg': round(o,4), 'count': c}
                    for p,o,c in bins_data
                ],
                'trained': self.model_weights.get('trained', False)
            }
        except Exception as e:
            return {'error': str(e)}

    def label_outcome(self, event_id: str, occurred: bool) -> bool:
        """Label an outcome (occurred / not occurred) for calibration and potential retraining."""
        try:
            if not os.path.isfile(self.calibration_store_path):
                return False
            with open(self.calibration_store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            updated = False
            for row in reversed(data):  # search from newest
                if row.get('event_id') == event_id and row.get('outcome') is None:
                    row['outcome'] = 1 if occurred else 0
                    row['labeled_at'] = datetime.utcnow().isoformat()
                    updated = True
                    break
            if updated:
                with open(self.calibration_store_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            return updated
        except Exception:
            return False

    def auto_label_elapsed_events(self):
        """Automatically label events whose scheduled time has passed as occurred if they remain unlabeled.
        Conservative heuristic; could be refined with external confirmations."""
        try:
            if not os.path.isfile(self.calibration_store_path):
                return 0
            with open(self.calibration_store_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            now = datetime.utcnow().replace(tzinfo=None)
            changed = 0
            for row in data:
                if row.get('outcome') is not None:
                    continue
                # parse scheduled time from factor set if available
                # (probability_explain endpoint returns predicted schedule, but we store only factors here)
                # fallback: treat predictions older than 48h as elapsed
                ts_str = row.get('timestamp')
                try:
                    if ts_str:
                        ts = datetime.fromisoformat(ts_str.replace('Z',''))
                        if (now - ts).total_seconds() > 48*3600:
                            row['outcome'] = 1  # assume occurred
                            row['auto_labeled'] = True
                            changed += 1
                except Exception:
                    continue
            if changed:
                with open(self.calibration_store_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            return changed
        except Exception:
            return 0

# Convenience singleton (optional)
_engine_singleton: Optional[EventProbabilityEngine] = None

def get_event_probability_engine() -> EventProbabilityEngine:
    global _engine_singleton
    if _engine_singleton is None:
        _engine_singleton = EventProbabilityEngine()
    return _engine_singleton
