def sma(values, window):
    if not values or window <= 0: return []
    out=[]
    for i in range(len(values)):
        start=max(0, i-window+1)
        segment=values[start:i+1]
        out.append(sum(segment)/len(segment))
    return out

def predict(prices):
    short=sma(prices, 5)
    long=sma(prices, 20)
    signal='hold'
    if len(prices) >= 20 and short[-1] > long[-1]: signal='buy'
    elif len(prices) >= 20 and short[-1] < long[-1]: signal='sell'
    return {'signal': signal, 'short': short[-1] if short else None, 'long': long[-1] if long else None}

def backtest(prices, short=5, long=20):
    cash=10000.0; position=0.0; last_price=None
    def _sma(vals, w):
        out=[]
        for i in range(len(vals)):
            start=max(0,i-w+1); seg=vals[start:i+1]; out.append(sum(seg)/len(seg))
        return out
    s=_sma(prices, short); l=_sma(prices, long)
    for i,p in enumerate(prices):
        last_price=p
        if i==0 or i>=len(l) or i>=len(s): continue
        if s[i] > l[i] and position==0:
            position=cash/p; cash=0
        elif s[i] < l[i] and position>0:
            cash=position*p; position=0
    final_value=cash if position==0 else cash+position*last_price
    return {'final_value': final_value}
