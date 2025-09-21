def score(prices, window=10):
    if not prices or len(prices)<window: return {'momentum': None}
    start=prices[-window]; end=prices[-1]
    if start==0: return {'momentum': None}
    return {'momentum': (end-start)/start}
