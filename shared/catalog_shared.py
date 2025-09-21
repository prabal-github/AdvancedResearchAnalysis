"""Shared catalog alias maps and simple in-memory persistence layer.

This module centralizes:
- Agent and model alias maps
- (Initial) in-memory subscription persistence with optional JSON file backing

If a database layer is available later, swap out SubscriptionStore implementation.
"""
from __future__ import annotations
import json
import threading
from pathlib import Path
from typing import Dict, Set, Optional, Any

# Alias maps (catalog id -> internal execution id)
AGENT_ALIAS_MAP: Dict[str, str] = {
    # Example mappings; extend as needed
    'momentum_intel': 'momentum_ai',
    'risk_guardian': 'risk_analyst',
    'alpha_scanner': 'alpha_finder',
    # Catalog agent IDs -> internal MLClass agent IDs
    'portfolio_risk_monitor': 'portfolio_risk',
    'regime_shift_detector': 'market_intelligence',  # maps macro regime detection to market intelligence agent
    'hedging_strategy_synth': 'trading_signals',     # strategy synth maps to trading signals generation
    'news_impact_ranker': 'market_intelligence',    # news impact contributes to market intelligence
    'portfolio_narrative_gen': 'client_advisory',   # narratives align with client advisory agent
}

MODEL_ALIAS_MAP: Dict[str, str] = {
    'multi_factor_forecaster': 'stock_predictor',
    'portfolio_risk_classifier': 'risk_classifier',
    'sentiment_nlp_model': 'sentiment_analyzer',
    # Catalog model IDs -> internal MLClass model IDs
    'intraday_drift': 'stock_predictor',
    'volatility_garch': 'risk_classifier',
    'regime_classifier': 'risk_classifier',  # treat regime classification as risk classification bucket
    'risk_parity': 'optimization_engine',
    'sentiment_transformer': 'sentiment_analyzer',
}

class SubscriptionStore:
    """Thread-safe in-memory subscription store with optional JSON persistence.

    Data shape:
    {
        'agents': set(...),
        'models': set(...)
    }
    """
    def __init__(self, persist_path: Optional[Path] = None):
        self._lock = threading.RLock()
        self._data = {'agents': set(), 'models': set()}
        self.persist_path = persist_path
        if persist_path and persist_path.exists():
            try:
                raw = json.loads(persist_path.read_text(encoding='utf-8'))
                self._data['agents'] = set(raw.get('agents', []))
                self._data['models'] = set(raw.get('models', []))
            except Exception:
                pass

    def save(self):
        if not self.persist_path:
            return
        with self._lock:
            tmp = {
                'agents': sorted(self._data['agents']),
                'models': sorted(self._data['models'])
            }
            try:
                self.persist_path.write_text(json.dumps(tmp, indent=2), encoding='utf-8')
            except Exception:
                pass

    def get(self) -> Dict[str, Set[str]]:
        with self._lock:
            return {'agents': set(self._data['agents']), 'models': set(self._data['models'])}

    def add(self, item_type: str, item_id: str):
        with self._lock:
            if item_type not in ('agent', 'model'):
                return False
            key = 'agents' if item_type == 'agent' else 'models'
            self._data[key].add(item_id)
            self.save()
            return True

    def remove(self, item_type: str, item_id: str):
        with self._lock:
            if item_type not in ('agent', 'model'):
                return False
            key = 'agents' if item_type == 'agent' else 'models'
            if item_id in self._data[key]:
                self._data[key].remove(item_id)
                self.save()
                return True
            return False

# Singleton accessor
_subscription_store: Optional[SubscriptionStore] = None

def get_subscription_store() -> SubscriptionStore:
    global _subscription_store
    if _subscription_store is None:
        path = Path(__file__).parent.parent / 'catalog_subscriptions.json'
        _subscription_store = SubscriptionStore(path)
    return _subscription_store

__all__ = [
    'AGENT_ALIAS_MAP', 'MODEL_ALIAS_MAP', 'SubscriptionStore', 'get_subscription_store'
]
