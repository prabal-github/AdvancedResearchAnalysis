def score(prices):
    if not prices or len(prices)<2: return {'vol': None}
    rets=[]
    for i in range(1,len(prices)):
        if prices[i-1]==0: continue
        rets.append((prices[i]-prices[i-1])/prices[i-1])
    if not rets: return {'vol': None}
    mean=sum(rets)/len(rets)
    var=sum((r-mean)**2 for r in rets)/len(rets)
    vol=var**0.5
    return {'vol': vol, 'n': len(rets)}
