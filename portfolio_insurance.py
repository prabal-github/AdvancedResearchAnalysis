"""Portfolio Insurance (Protective Put / Collar) Skeleton

Purpose:
  Provide a framework to create a time‑bounded "insurance" policy for an equity / ETF portfolio
  by dynamically sizing index option hedges (e.g. NIFTY / BANKNIFTY / SPX) using current holdings
  & beta-adjusted exposure. Uses:
    - yfinance for current prices (fallback / initial beta estimation)
    - Upstox (placeholder) for live options chain + order placement

DISCLAIMER: This is a simplified educational scaffold. Real production implementation requires
 market microstructure handling, slippage modeling, regulatory compliance, margin, taxation.

Key Concepts:
  * Policy: Defines coverage window [start, end], floor (e.g. max drawdown 10%), target index, strategy type.
  * Hedge Sizing: Notional_hedged = Portfolio_Value * Coverage_Ratio (e.g. 0.9 floor => hedge 10% tail or full protective put)
  * Instruments: Protective Put (default) or Cost‑Reduced Collar (buy put, sell OTM call).
  * Monitoring: Revalue portfolio & hedge daily (or intraday) and record MTM & breach status.
  * Settlement: At expiry or early trigger, compute payoff (put intrinsic) vs insured floor gap.

Suggested DB Integration (not implemented here):
  Table: insurance_policies(id, user_id, status, created_at, start_utc, end_utc, floor_pct, index_symbol,
                            strategy, put_strike, call_strike, contracts_put, contracts_call, premium_paid,
                            coverage_notional, portfolio_value_at_bind, beta, notes, last_nav, breach_flag)

Usage Flow:
  1. Take portfolio snapshot (positions + prices) -> compute total value & index beta.
  2. Determine coverage params (floor_pct, term_days, strategy='protective_put'|'collar').
  3. Fetch option chain for target expiry >= end date.
  4. Select strikes (put near floor, optional call for collar) & size contracts.
  5. Return policy draft -> confirm -> place orders (Upstox) -> persist in DB.
  6. Schedule monitor tasks -> on expiry settle.

"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import math

try:
    import yfinance as yf  # type: ignore
except ImportError:  # lightweight fallback
    yf = None  # noqa

# ------------------------- Data Structures -------------------------
@dataclass
class Position:
    symbol: str
    quantity: float
    asset_type: str = "equity"  # equity|etf|cash
    beta: Optional[float] = None  # optional precomputed beta vs index

@dataclass
class OptionQuote:
    symbol: str  # e.g. NIFTY24SEP18000PE
    expiry: datetime
    strike: float
    option_type: str  # 'PUT' | 'CALL'
    last_price: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    underlying: Optional[str] = None

@dataclass
class HedgeLeg:
    option: OptionQuote
    contracts: int
    side: str  # 'BUY' or 'SELL'
    est_cost: float

@dataclass
class PolicyDraft:
    portfolio_value: float
    beta: float
    coverage_notional: float
    floor_pct: float
    start_utc: datetime
    end_utc: datetime
    strategy: str
    index_symbol: str
    put_leg: HedgeLeg
    call_leg: Optional[HedgeLeg]
    premium_net: float
    metadata: Dict[str, Any] = field(default_factory=dict)

# ------------------------- Core Calculations -------------------------

def estimate_portfolio_beta(positions: List[Position], index_symbol: str) -> float:
    """Simplified beta estimation placeholder.
    Real implementation: regress portfolio daily returns vs index over lookback window.
    Here: average provided per-position beta (fallback=1.0).
    """
    betas = [p.beta for p in positions if p.beta is not None]
    if betas:
        return sum(betas) / len(betas)
    return 1.0  # conservative default


def compute_portfolio_value(positions: List[Position], price_map: Dict[str, float]) -> float:
    total = 0.0
    for p in positions:
        px = price_map.get(p.symbol)
        if px is None:
            continue
        total += px * p.quantity
    return total


def required_put_notional(portfolio_value: float, floor_pct: float) -> float:
    """Amount of value to protect. floor_pct e.g. 0.90 means insure drop below 90% => protection portion ~ (1-floor_pct).*value.
    For full protective put (cover delta ~1), hedge notional ~ portfolio_value * beta.
    Choose conservative approach: hedge full portfolio value * beta.
    """
    return portfolio_value  # can adjust to (1 - floor_pct) * portfolio_value for partial coverage


def select_put_strike(index_level: float, floor_pct: float) -> float:
    # Strike approximated at floor level (rounded to nearest 50 / 100 multiple typical for index)
    raw = index_level * floor_pct
    # Round to nearest 50
    return round(raw / 50) * 50


def select_call_strike(index_level: float, upside_cap_pct: float = 1.05) -> float:
    raw = index_level * upside_cap_pct
    return round(raw / 50) * 50


def contracts_needed(notional: float, index_level: float, contract_multiplier: int) -> int:
    return math.ceil(notional / (index_level * contract_multiplier))

# ------------------------- External Data (Placeholders) -------------------------

def fetch_index_level(symbol: str) -> float:
    if yf:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            return float(data['Close'].iloc[-1])
    # Fallback static placeholder
    return 20000.0


def fetch_option_chain(upstox_client, index_symbol: str, expiry: datetime) -> List[OptionQuote]:  # type: ignore
    """Placeholder for Upstox options chain fetch.
    Real call: upstox_client.get_option_chain(index_symbol, expiry)
    Return minimal synthetic sample here.
    """
    base = fetch_index_level(index_symbol)
    strikes = [base * s for s in [0.9, 0.95, 1.0, 1.05, 1.1]]
    quotes: List[OptionQuote] = []
    for k in strikes:
        k_round = round(k / 50) * 50
        quotes.append(OptionQuote(symbol=f"{index_symbol}{expiry:%y%m%d}{int(k_round)}PE", expiry=expiry, strike=k_round, option_type='PUT', last_price=max(1.0, (k_round - base) * 0.4 * -1)))
        quotes.append(OptionQuote(symbol=f"{index_symbol}{expiry:%y%m%d}{int(k_round)}CE", expiry=expiry, strike=k_round, option_type='CALL', last_price=max(1.0, (base - k_round) * 0.35 * -1)))
    return quotes

# ------------------------- Draft Policy Construction -------------------------

def build_policy_draft(
    positions: List[Position],
    price_map: Dict[str, float],
    floor_pct: float,
    term_days: int,
    index_symbol: str = "^NSEI",  # NIFTY index (yfinance)
    strategy: str = "protective_put",
    contract_multiplier: int = 50,
    upside_cap_pct: float = 1.05,
    upstox_client=None,
) -> PolicyDraft:
    start = datetime.utcnow()
    end = start + timedelta(days=term_days)
    beta = estimate_portfolio_beta(positions, index_symbol)
    portfolio_value = compute_portfolio_value(positions, price_map)
    index_level = fetch_index_level(index_symbol)
    coverage_notional = required_put_notional(portfolio_value * beta, floor_pct)

    # Option selection
    expiry = end  # Simplify: choose expiry at/after end
    chain = fetch_option_chain(upstox_client, index_symbol, expiry)
    put_strike = select_put_strike(index_level, floor_pct)
    put_quotes = [q for q in chain if q.option_type == 'PUT' and q.strike == put_strike]
    if not put_quotes:
        raise ValueError("Desired put strike not available in chain")
    put_q = put_quotes[0]
    put_contracts = contracts_needed(coverage_notional, index_level, contract_multiplier)
    put_cost_est = put_q.last_price * contract_multiplier * put_contracts
    put_leg = HedgeLeg(option=put_q, contracts=put_contracts, side='BUY', est_cost=put_cost_est)

    call_leg: Optional[HedgeLeg] = None
    premium_net = put_cost_est
    if strategy == 'collar':
        call_strike = select_call_strike(index_level, upside_cap_pct)
        call_quotes = [q for q in chain if q.option_type == 'CALL' and q.strike == call_strike]
        if call_quotes:
            call_q = call_quotes[0]
            call_contracts = put_contracts  # match notional
            call_prem = call_q.last_price * contract_multiplier * call_contracts
            call_leg = HedgeLeg(option=call_q, contracts=call_contracts, side='SELL', est_cost=-call_prem)
            premium_net = put_cost_est - call_prem

    md = {
        'index_level': index_level,
        'put_strike': put_strike,
        'term_days': term_days,
        'contract_multiplier': contract_multiplier,
        'beta': beta,
    }
    return PolicyDraft(
        portfolio_value=portfolio_value,
        beta=beta,
        coverage_notional=coverage_notional,
        floor_pct=floor_pct,
        start_utc=start,
        end_utc=end,
        strategy=strategy,
        index_symbol=index_symbol,
        put_leg=put_leg,
        call_leg=call_leg,
        premium_net=premium_net,
        metadata=md,
    )

# ------------------------- Settlement Logic (Simplified) -------------------------

def estimate_policy_payoff(policy: PolicyDraft, final_portfolio_value: float, final_index_level: float) -> Dict[str, Any]:
    """Compute indicative payoff of the hedge vs shortfall below floor.
    Protective put intrinsic: max(0, put_strike - final_index_level) * multiplier * contracts
    Shortfall: max(0, policy.floor_pct * initial_value - final_portfolio_value)
    Payout limited to whichever mechanism chosen (here: intrinsic acts as compensation proxy).
    """
    mult = policy.metadata.get('contract_multiplier', 50)
    put_strike = policy.put_leg.option.strike
    intrinsic = max(0.0, put_strike - final_index_level) * mult * policy.put_leg.contracts
    floor_value = policy.floor_pct * policy.portfolio_value
    shortfall = max(0.0, floor_value - final_portfolio_value)
    effective_comp = min(intrinsic, shortfall)
    return {
        'put_intrinsic_value': intrinsic,
        'portfolio_shortfall': shortfall,
        'compensation': effective_comp,
        'net_result_after_hedge': final_portfolio_value + effective_comp,
        'initial_portfolio_value': policy.portfolio_value,
        'floor_value': floor_value,
        'premium_net': policy.premium_net,
    }

# ------------------------- Example Usage (manual test) -------------------------
if __name__ == '__main__':
    sample_positions = [
        Position(symbol='AAPL', quantity=10, beta=1.1),
        Position(symbol='MSFT', quantity=8, beta=1.0),
        Position(symbol='SPY', quantity=5, beta=1.0),
    ]
    # Mock prices
    prices = {'AAPL': 210, 'MSFT': 430, 'SPY': 560}
    draft = build_policy_draft(sample_positions, prices, floor_pct=0.9, term_days=30, strategy='collar')
    print('Draft Policy:')
    print(draft)
    payoff = estimate_policy_payoff(draft, final_portfolio_value=draft.portfolio_value * 0.88, final_index_level=fetch_index_level(draft.index_symbol) * 0.9)
    print('Estimated Payoff:')
    print(payoff)
