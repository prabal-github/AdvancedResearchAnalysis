import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration
stocks = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", 
    "AXISBANK.NS", "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", 
    "BEL.NS", "BPCL.NS", "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", 
    "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "GRASIM.NS", 
    "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HEROMOTOCO.NS", 
    "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS"
]

# Cache data to improve performance
def get_stock_data(symbol, period='1mo'):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

# Technical Indicators (No TA-Lib)
def calculate_rsi(prices, window=14):
    deltas = np.diff(prices)
    seed = deltas[:window+1]
    up = seed[seed >= 0].sum()/window
    down = -seed[seed < 0].sum()/window
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:window] = 100. - 100./(1.+rs)

    for i in range(window, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(window-1) + upval)/window
        down = (down*(window-1) + downval)/window
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi[-1]

def calculate_macd(prices, slow=26, fast=12):
    ema_fast = prices.ewm(span=fast, adjust=False).mean().values[-1]
    ema_slow = prices.ewm(span=slow, adjust=False).mean().values[-1]
    return ema_fast - ema_slow

def calculate_bollinger_bands(prices, window=20, num_std=2):
    sma = prices.rolling(window).mean().values[-1]
    rolling_std = prices.rolling(window).std().values[-1]
    upper = sma + (rolling_std * num_std)
    lower = sma - (rolling_std * num_std)
    return upper, lower

def calculate_atr(high, low, close, window=14):
    tr = np.maximum(high - low, 
                   np.maximum(np.abs(high - close), 
                             np.abs(low - close)))
    return tr.rolling(window).mean().values[-1]

def detect_candlestick_pattern(open_price, high, low, close):
    body_size = abs(close - open_price)
    upper_shadow = high - max(open_price, close)
    lower_shadow = min(open_price, close) - low
    
    patterns = []
    
    # Bullish Patterns
    if lower_shadow > 2 * body_size and upper_shadow < body_size * 0.1:
        patterns.append("Hammer (Bullish)")
    if close > open_price and body_size > 0 and \
       close > (high + low)/2 and lower_shadow > upper_shadow:
        patterns.append("Bullish Engulfing")
    
    # Bearish Patterns
    if upper_shadow > 2 * body_size and lower_shadow < body_size * 0.1:
        patterns.append("Shooting Star (Bearish)")
    if close < open_price and body_size > 0 and \
       close < (high + low)/2 and upper_shadow > lower_shadow:
        patterns.append("Bearish Engulfing")
    
    return patterns if patterns else None

def calculate_tsi(prices, short=13, long=25):
    diff = np.diff(prices)
    ema_short = pd.Series(diff).ewm(span=short, adjust=False).mean().values[-1]
    ema_long = pd.Series(ema_short).ewm(span=long, adjust=False).mean().values[-1]
    abs_diff = np.abs(diff)
    ema_abs_short = pd.Series(abs_diff).ewm(span=short, adjust=False).mean().values[-1]
    ema_abs_long = pd.Series(ema_abs_short).ewm(span=long, adjust=False).mean().values[-1]
    return 100 * (ema_long / ema_abs_long) if ema_abs_long != 0 else 0

def detect_support_resistance(prices, threshold=0.02):
    resistance = prices.rolling(20).max().values[-1]
    support = prices.rolling(20).min().values[-1]
    current = prices.values[-1]
    
    if current >= resistance * (1 - threshold):
        return "Near Resistance (Bearish)"
    elif current <= support * (1 + threshold):
        return "Near Support (Bullish)"
    return None

# BTST Strategy Analysis Metrics
def calculate_btst_metrics(hist):
    if len(hist) < 2:
        return None, None, None, None, None
    
    # Get today's and previous day's data
    today = hist.iloc[-1]
    prev_day = hist.iloc[-2]
    
    # Calculate BTST metrics
    price_change_pct = ((today['Close'] - today['Open']) / today['Open']) * 100
    close_near_high = ((today['Close'] - today['Low']) / (today['High'] - today['Low'])) * 100 if (today['High'] - today['Low']) > 0 else 0
    intraday_range_pct = ((today['High'] - today['Low']) / today['Open']) * 100
    close_above_prev_high = today['Close'] > prev_day['High']
    
    # Calculate volume spike
    avg_volume = hist['Volume'].rolling(window=min(20, len(hist))).mean().iloc[-1]
    volume_spike = (today['Volume'] / avg_volume) if avg_volume > 0 else 0
    
    # Calculate BTST score
    btst_score = 0
    btst_score += 25 if close_above_prev_high else 0
    btst_score += 25 if close_near_high >= 70 else 0
    btst_score += 25 if volume_spike > 1.5 else 0
    btst_score += 25 if intraday_range_pct > 2 else 0
    
    return {
        'Price Change (%)': round(price_change_pct, 2),
        'Close Near High (%)': round(close_near_high, 2),
        'Intraday Range (%)': round(intraday_range_pct, 2),
        'Volume Spike': round(volume_spike, 2),
        'Close > Prev High': 'Yes' if close_above_prev_high else 'No',
        'BTST Score': btst_score
    }

# Calculate BTST-specific stop loss and target
def calculate_btst_risk_management(latest, prev_day, atr):
    # Base stop loss and target on ATR
    stop_loss = round(latest['Close'] - atr * 1.5, 2)
    target = round(latest['Close'] + atr * 3, 2)
    
    # Adjust based on intraday range
    intraday_range = latest['High'] - latest['Low']
    if intraday_range > 0:
        # Tighten stop loss for volatile stocks
        stop_loss = max(stop_loss, round(latest['Close'] - intraday_range * 0.75, 2))
        
        # Adjust target based on close position relative to high
        close_position = (latest['Close'] - latest['Low']) / intraday_range
        if close_position > 0.8:  # Closed near high
            target = round(latest['Close'] + intraday_range * 1.5, 2)
    
    # Ensure target is at least 1.5x risk
    risk = latest['Close'] - stop_loss
    reward = target - latest['Close']
    if reward < risk * 1.5:
        target = round(latest['Close'] + risk * 2.0, 2)
    
    return stop_loss, target

def analyze_stock(symbol):
    try:
        # Get data
        hist = get_stock_data(symbol, period='5d')  # Reduced to 5 days for BTST
        if hist is None or hist.empty:
            return None
        
        # Extract latest data
        latest = hist.iloc[-1]
        prev_day = hist.iloc[-2] if len(hist) > 1 else latest
        
        # Calculate indicators
        close_prices = hist['Close']
        rsi = calculate_rsi(close_prices.values)
        macd = calculate_macd(close_prices)
        upper_bb, lower_bb = calculate_bollinger_bands(close_prices)
        atr = calculate_atr(hist['High'], hist['Low'], hist['Close'])
        tsi_value = calculate_tsi(close_prices.values)
        candlestick_patterns = detect_candlestick_pattern(
            latest['Open'], latest['High'], latest['Low'], latest['Close'])
        sr_level = detect_support_resistance(close_prices)
        
        # Calculate BTST metrics
        btst_metrics = calculate_btst_metrics(hist)
        
        # Calculate price change
        price_change = ((latest['Close'] - prev_day['Close']) / prev_day['Close']) * 100
        
        # Initialize confidence and models used
        confidence = 50
        models_used = {}
        
        # 1. Primary Open-High/Low Condition
        if latest['Open'] == latest['High']:
            primary_signal = "Sell"
            confidence = max(confidence, 70)
            stop_loss = round(latest['Close'] * 1.02, 2)
            target = round(latest['Close'] * 0.96, 2)
            condition = "Open=High (Bearish)"
            models_used['Open-High'] = {'signal': 'Bearish', 'confidence': 30}
        elif latest['Open'] == latest['Low']:
            primary_signal = "Buy"
            confidence = max(confidence, 70)
            stop_loss = round(latest['Close'] * 0.98, 2)
            target = round(latest['Close'] * 1.04, 2)
            condition = "Open=Low (Bullish)"
            models_used['Open-Low'] = {'signal': 'Bullish', 'confidence': 30}
        else:
            primary_signal = "Neutral"
            condition = "No clear Open-High/Low pattern"
            stop_loss = None
            target = None
        
        # 2. Candlestick Patterns
        if candlestick_patterns:
            for pattern in candlestick_patterns:
                if "Bullish" in pattern:
                    models_used[f'Candlestick ({pattern})'] = {'signal': 'Bullish', 'confidence': 15}
                    if primary_signal == "Neutral":
                        confidence += 15
                elif "Bearish" in pattern:
                    models_used[f'Candlestick ({pattern})'] = {'signal': 'Bearish', 'confidence': 15}
                    if primary_signal == "Neutral":
                        confidence -= 15
        
        # 3. RSI Analysis
        if rsi > 70:
            models_used['RSI'] = {'signal': 'Overbought', 'confidence': 10}
            confidence -= 10
        elif rsi < 30:
            models_used['RSI'] = {'signal': 'Oversold', 'confidence': 10}
            confidence += 10
        
        # 4. MACD Analysis
        if macd > 0:
            models_used['MACD'] = {'signal': 'Bullish', 'confidence': 10}
            confidence += 10
        else:
            models_used['MACD'] = {'signal': 'Bearish', 'confidence': 10}
            confidence -= 10
        
        # 5. Bollinger Bands
        if latest['Close'] > upper_bb:
            models_used['Bollinger Bands'] = {'signal': 'Overbought', 'confidence': 10}
            confidence -= 10
        elif latest['Close'] < lower_bb:
            models_used['Bollinger Bands'] = {'signal': 'Oversold', 'confidence': 10}
            confidence += 10
        
        # 6. TSI Analysis
        if tsi_value > 25:
            models_used['TSI'] = {'signal': 'Bullish', 'confidence': 10}
            confidence += 10
        elif tsi_value < -25:
            models_used['TSI'] = {'signal': 'Bearish', 'confidence': 10}
            confidence -= 10
        
        # 7. Support/Resistance
        if sr_level:
            if "Support" in sr_level:
                models_used['Support/Resistance'] = {'signal': 'Bullish', 'confidence': 10}
                confidence += 10
            elif "Resistance" in sr_level:
                models_used['Support/Resistance'] = {'signal': 'Bearish', 'confidence': 10}
                confidence -= 10
        
        # 8. BTST Strategy Scoring
        btst_signal = False
        if btst_metrics and btst_metrics['BTST Score'] > 75:
            models_used['BTST'] = {'signal': 'Bullish', 'confidence': 30}
            confidence += 30
            btst_signal = True
            # Override recommendation if BTST score is high
            if primary_signal == "Neutral" and confidence > 60:
                primary_signal = "BTST Buy"
        
        # Determine final recommendation
        if confidence >= 70:
            recommendation = "Buy" if confidence >= 70 else "Sell"
        elif confidence <= 30:
            recommendation = "Sell"
        else:
            recommendation = "Neutral"
            
        # Special case for BTST recommendations
        if btst_signal:
            recommendation = "BTST Buy"
        
        # Calculate stop loss and target if not set by primary signal
        if stop_loss is None and recommendation != "Neutral":
            if recommendation == "Buy":
                stop_loss = round(latest['Close'] - atr * 1.5, 2)
                target = round(latest['Close'] + atr * 3, 2)
            elif recommendation == "BTST Buy":
                # Use specialized BTST risk management
                stop_loss, target = calculate_btst_risk_management(latest, prev_day, atr)
            else:  # Sell
                stop_loss = round(latest['Close'] + atr * 1.5, 2)
                target = round(latest['Close'] - atr * 3, 2)
        
        # Cap confidence
        confidence = max(0, min(100, confidence))
        
        # Prepare result dictionary
        result = {
            'Symbol': symbol,
            'Current Price': round(latest['Close'], 2),
            'Change (%)': round(price_change, 2),
            'Open': round(latest['Open'], 2),
            'High': round(latest['High'], 2),
            'Low': round(latest['Low'], 2),
            'Volume': f"{latest['Volume']:,.0f}",
            'RSI (14)': round(rsi, 2),
            'MACD': round(macd, 4),
            'Bollinger Bands': f"{round(lower_bb, 2)}-{round(upper_bb, 2)}",
            'ATR': round(atr, 2),
            'TSI': round(tsi_value, 2),
            'Candlestick': candlestick_patterns[0] if candlestick_patterns else None,
            'Support/Resistance': sr_level,
            'Recommendation': recommendation,
            'Confidence (%)': round(confidence),
            'Stop Loss': stop_loss,
            'Target': target,
            'Primary Condition': condition,
            'Models Used': models_used,
            'Last Updated': latest.name.strftime('%Y-%m-%d %H:%M')
        }
        
        # Add BTST metrics to result
        if btst_metrics:
            result.update(btst_metrics)
        
        return result
        
    except Exception as e:
        print(f"Error analyzing {symbol}: {str(e)}")
        return None

def main():
    print("Starting stock analysis...")
    min_confidence = 70  # Minimum confidence threshold
    btst_threshold = 75  # BTST score threshold
    
    # Analyze stocks
    results = []
    for symbol in stocks:
        print(f"Analyzing {symbol}...")
        result = analyze_stock(symbol)
        if result:
            results.append(result)
    
    if not results:
        print("No valid data could be fetched. Try again later.")
        return
    
    # Create results DataFrame
    results_df = pd.DataFrame(results)
    
    # Filter actionable recommendations
    actionable_df = results_df[
        (results_df['Recommendation'].isin(['Buy', 'Sell', 'BTST Buy'])) & 
        (results_df['Confidence (%)'] >= min_confidence)
    ].sort_values('Confidence (%)', ascending=False)
    
    # Filter BTST opportunities
    btst_df = actionable_df[
        (actionable_df['BTST Score'] >= btst_threshold) & 
        (actionable_df['Recommendation'] == 'BTST Buy')
    ].sort_values('BTST Score', ascending=False)
    
    # Display results
    print("\n Analysis Results")
    print(f"Analyzed {len(results_df)} stocks")
    print(f"Found {len(actionable_df)} actionable recommendations")
    print(f"Found {len(btst_df)} BTST opportunities")
    print(f"Average confidence: {results_df['Confidence (%)'].mean():.1f}%")
    
    # BTST Opportunities
    print("\n BTST Opportunities (Buy Today, Sell Tomorrow)")
    if not btst_df.empty:
        btst_cols = ['Symbol', 'Current Price', 'BTST Score', 'Stop Loss', 'Target', 
                   'Price Change (%)', 'Close Near High (%)', 'Intraday Range (%)', 
                   'Volume Spike', 'Close > Prev High', 'Confidence (%)']
        
        print(btst_df[btst_cols].sort_values('BTST Score', ascending=False).to_string())
        
        # Calculate risk-reward ratio
        btst_df['Risk'] = btst_df['Current Price'] - btst_df['Stop Loss']
        btst_df['Reward'] = btst_df['Target'] - btst_df['Current Price']
        btst_df['Risk-Reward'] = btst_df['Reward'] / btst_df['Risk']
        
        avg_risk_reward = btst_df['Risk-Reward'].mean()
        print(f"\nAverage Risk-Reward Ratio: {avg_risk_reward:.2f}:1")
    else:
        print("No strong BTST opportunities found based on current criteria.")
    
    # Actionable Recommendations
    print("\n Top Recommendations")
    if not actionable_df.empty:
        display_cols = ['Symbol', 'Current Price', 'Change (%)', 'Recommendation', 
                      'Confidence (%)', 'Stop Loss', 'Target', 'Primary Condition']
        
        print(actionable_df[display_cols].sort_values('Confidence (%)', ascending=False).to_string())
    else:
        print("No strong recommendations meet your confidence threshold.")

if __name__ == "__main__":
    main()