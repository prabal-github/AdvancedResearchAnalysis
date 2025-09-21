"""Quick validation that SELL recommendations have stop loss above target (short logic)."""
from models.overnight_edge_btst import OvernightEdgeBTSTAnalyzer
import pandas as pd

a = OvernightEdgeBTSTAnalyzer()
# synthetic data to force SELL (Open=High)
latest = pd.Series({'Open':100,'High':100,'Low':95,'Close':98,'Volume':1_000_000})
prev = pd.Series({'Open':99,'High':101,'Low':94,'Close':99,'Volume':900_000})
sl,tgt = a.calculate_btst_risk_management(latest, prev, atr=2.0, side='SHORT')
assert sl > tgt, f"Stop loss {sl} should be > target {tgt} for SHORT"
print('PASS short logic ordering sl>tgt', sl, tgt)

sl2,tgt2 = a.calculate_btst_risk_management(latest, prev, atr=2.0, side='LONG')
assert tgt2 > sl2, f"Target {tgt2} should be > stop loss {sl2} for LONG"
print('PASS long logic ordering tgt>sl', sl2, tgt2)
