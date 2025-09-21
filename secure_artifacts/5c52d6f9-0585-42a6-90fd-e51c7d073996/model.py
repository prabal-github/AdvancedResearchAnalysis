import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class GapFillProbabilityModel:
    def __init__(self, symbols):
        self.symbols = symbols
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=180)  # 1 year data
        
    def download_data(self):
        """Download historical price data"""
        print("Downloading stock data for gap analysis...")
        
        # Download data for each symbol individually to avoid multi-index issues
        close_prices = pd.DataFrame()
        high_prices = pd.DataFrame()
        low_prices = pd.DataFrame()
        
        for symbol in self.symbols:
            try:
                print(f"Downloading {symbol}...")
                data = yf.download(symbol, start=self.start_date, end=self.end_date, progress=False)
                
                if not data.empty:
                    close_prices[symbol] = data['Close']
                    high_prices[symbol] = data['High']
                    low_prices[symbol] = data['Low']
                else:
                    print(f"No data found for {symbol}")
                    
            except Exception as e:
                print(f"Error downloading {symbol}: {e}")
                continue
        
        return close_prices, high_prices, low_prices
    
    def calculate_gaps(self, close_prices, high_prices, low_prices):
        """Calculate gap percentages and probabilities"""
        results = []
        
        for symbol in self.symbols:
            try:
                if symbol not in close_prices.columns:
                    continue
                    
                # Get recent data
                closes = close_prices[symbol].dropna()
                highs = high_prices[symbol].dropna()
                lows = low_prices[symbol].dropna()
                
                if len(closes) < 20:  # Minimum data check
                    print(f"Skipping {symbol}: insufficient data ({len(closes)} points)")
                    continue
                
                # Current gap calculation (using last two available days)
                if len(closes) >= 2:
                    current_close = closes.iloc[-2]  # Previous day close
                    current_open = closes.iloc[-1]   # Current day price (using close as proxy)
                    current_gap = ((current_open - current_close) / current_close) * 100
                else:
                    print(f"Skipping {symbol}: not enough recent data")
                    continue
                
                # Historical gap analysis
                gap_fill_stats = self.analyze_historical_gaps(closes, highs, lows)
                
                # Current gap classification
                gap_type = self.classify_gap(current_gap)
                
                # Fill probability estimation
                fill_probability = self.estimate_fill_probability(current_gap, gap_fill_stats)
                
                # Target levels
                targets = self.calculate_target_levels(current_gap, current_close, current_open)
                
                results.append({
                    'Symbol': symbol,
                    'Previous_Close': round(current_close, 2),
                    'Current_Price': round(current_open, 2),
                    'Gap_Percentage': round(current_gap, 2),
                    'Gap_Type': gap_type,
                    'Fill_Probability_%': round(fill_probability, 1),
                    'Gap_Fill_Target': round(targets['fill_target'], 2),
                    'Stop_Loss': round(targets['stop_loss'], 2),
                    'Avg_Fill_Time_Days': round(gap_fill_stats['avg_fill_time'], 1),
                    'Fill_Rate_%': round(gap_fill_stats['fill_rate'] * 100, 1),
                    'Total_Gaps_Analyzed': gap_fill_stats['total_gaps']
                })
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {str(e)}")
                continue
        
        return pd.DataFrame(results)
    
    def analyze_historical_gaps(self, closes, highs, lows):
        """Analyze historical gap patterns"""
        gaps = []
        fill_times = []
        filled_count = 0
        total_gaps = 0
        
        for i in range(2, len(closes)):  # Start from index 2 to have previous close
            try:
                prev_close = closes.iloc[i-1]
                current_price = closes.iloc[i]  # Using close as proxy for open
                
                gap = ((current_price - prev_close) / prev_close) * 100
                
                if abs(gap) > 0.5:  # Consider gaps > 0.5%
                    total_gaps += 1
                    gap_direction = 1 if gap > 0 else -1
                    filled, fill_time = self.check_gap_fill(
                        gap, gap_direction, i, closes, highs, lows
                    )
                    
                    if filled:
                        filled_count += 1
                        fill_times.append(fill_time)
                    
                    gaps.append({
                        'gap_size': abs(gap),
                        'direction': gap_direction,
                        'filled': filled,
                        'fill_time': fill_time
                    })
            except:
                continue
        
        fill_rate = filled_count / total_gaps if total_gaps > 0 else 0
        avg_fill_time = np.mean(fill_times) if fill_times else 0
        
        return {
            'fill_rate': fill_rate,
            'avg_fill_time': avg_fill_time,
            'total_gaps': total_gaps
        }
    
    def check_gap_fill(self, gap, direction, start_idx, closes, highs, lows):
        """Check if a gap was filled within 10 days"""
        try:
            gap_size = abs(gap)
            target_level = closes.iloc[start_idx-1]  # Pre-gap close
            
            for j in range(start_idx, min(start_idx + 10, len(closes))):
                if direction > 0:  # Gap up
                    if lows.iloc[j] <= target_level:
                        return True, j - start_idx
                else:  # Gap down
                    if highs.iloc[j] >= target_level:
                        return True, j - start_idx
            
            return False, 10  # Not filled within 10 days
        except:
            return False, 10
    
    def classify_gap(self, gap_percentage):
        """Classify gap based on size"""
        abs_gap = abs(gap_percentage)
        
        if abs_gap < 0.5:
            return "Minor"
        elif abs_gap < 2.0:
            return "Normal"
        elif abs_gap < 5.0:
            return "Significant"
        else:
            return "Major"
    
    def estimate_fill_probability(self, current_gap, historical_stats):
        """Estimate probability of gap fill"""
        abs_gap = abs(current_gap)
        
        # Default probabilities based on gap size if no historical data
        if historical_stats['total_gaps'] == 0:
            if abs_gap < 1.0:
                return 85.0
            elif abs_gap < 2.0:
                return 70.0
            elif abs_gap < 3.0:
                return 55.0
            else:
                return 35.0
        
        base_probability = historical_stats['fill_rate'] * 100
        
        # Adjust probability based on gap size
        if abs_gap < 1.0:
            probability = min(95, base_probability * 1.2)
        elif abs_gap < 2.0:
            probability = base_probability
        elif abs_gap < 3.0:
            probability = max(40, base_probability * 0.8)
        else:
            probability = max(20, base_probability * 0.6)
        
        # Adjust for gap direction (gaps up tend to fill less frequently)
        if current_gap > 0:
            probability *= 0.9
        
        return min(95, max(5, probability))
    
    def calculate_target_levels(self, gap_percentage, previous_close, current_price):
        """Calculate target and stop loss levels"""
        if gap_percentage > 0:  # Gap up
            fill_target = previous_close  # Gap fill level
            stop_loss = current_price * 0.98  # 2% below current price
        else:  # Gap down
            fill_target = previous_close  # Gap fill level
            stop_loss = current_price * 1.02  # 2% above current price
        
        return {
            'fill_target': fill_target,
            'stop_loss': stop_loss
        }
    
    def generate_signals(self, results_df):
        """Generate trading signals based on gap analysis"""
        signals = []
        
        for _, row in results_df.iterrows():
            gap = row['Gap_Percentage']
            prob = row['Fill_Probability_%']
            
            if abs(gap) < 0.3:  # Very small gap
                signals.append('Ignore')
            elif gap > 0:  # Gap up
                if prob > 65:
                    signals.append('Short (Gap Fill Expected)')
                else:
                    signals.append('Hold (Gap May Not Fill)')
            else:  # Gap down
                if prob > 65:
                    signals.append('Long (Gap Fill Expected)')
                else:
                    signals.append('Hold (Gap May Not Fill)')
        
        results_df['Signal'] = signals
        return results_df
    
    def run_analysis(self):
        """Run complete gap analysis"""
        try:
            close_prices, high_prices, low_prices = self.download_data()
            
            if close_prices.empty:
                print("No data downloaded. Please check your internet connection.")
                return None
            
            print(f"Successfully downloaded data for {len(close_prices.columns)} symbols")
            
            results = self.calculate_gaps(close_prices, high_prices, low_prices)
            
            if results.empty:
                print("No gap analysis results generated.")
                return None
                
            results = self.generate_signals(results)
            
            # Sort by gap size (absolute value)
            results['Abs_Gap'] = results['Gap_Percentage'].abs()
            results = results.sort_values('Abs_Gap', ascending=False)
            results = results.drop('Abs_Gap', axis=1)
            
            return results
            
        except Exception as e:
            print(f"Error in gap analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

def main():
    # Nifty 50 stocks
    symbols = [
        "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
        "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BPCL.NS",
        "BHARTIARTL.NS", "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS",
        "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
        "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
        "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
        "M&M.NS", "MARUTI.NS", "NTPC.NS", "NESTLEIND.NS", "ONGC.NS",
        "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS",
        "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS",
        "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS"
    ]
    
    print("Gap Fill Probability Analysis")
    print("=" * 100)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    
    # Initialize and run analysis
    gap_analyzer = GapFillProbabilityModel(symbols)
    results = gap_analyzer.run_analysis()
    
    if results is not None and not results.empty:
        # Display results with significant gaps first
        print("\nGAP ANALYSIS RESULTS (Sorted by Gap Size):")
        print("=" * 100)
        
        # Format display columns
        display_cols = [
            'Symbol', 'Gap_Percentage', 'Gap_Type', 'Fill_Probability_%',
            'Signal', 'Previous_Close', 'Current_Price', 'Gap_Fill_Target'
        ]
        
        formatted_df = results[display_cols].copy()
        formatted_df.columns = [
            'Symbol', 'Gap %', 'Type', 'Fill Prob%', 
            'Signal', 'Prev Close', 'Current', 'Fill Target'
        ]
        
        print(formatted_df.to_string(index=False, float_format=lambda x: f'{x:.2f}'))
        
        # Summary statistics
        print("\n" + "=" * 100)
        print("SUMMARY STATISTICS:")
        print("=" * 100)
        print(f"Total stocks analyzed: {len(results)}")
        print(f"Stocks with significant gaps (>1%): {len(results[results['Gap_Percentage'].abs() > 1])}")
        print(f"Average fill probability: {results['Fill_Probability_%'].mean():.1f}%")
        
        # Count signals
        signal_counts = results['Signal'].value_counts()
        print("\nSignal Distribution:")
        for signal, count in signal_counts.items():
            print(f"{signal}: {count} stocks")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gap_fill_analysis_{timestamp}.csv"
        results.to_csv(filename, index=False)
        print(f"\nResults saved to: {filename}")
        
    else:
        print("No results generated. Please check data availability.")

def run_analysis_demo(max_stocks=5):
    """Quick demo version with limited stocks"""
    model = globals()[list(globals().keys())[-1]]()  # Get the model class
    if hasattr(model, 'stocks'):
        model.stocks = model.stocks[:max_stocks]
    if hasattr(model, 'run_analysis'):
        return model.run_analysis()
    return "Demo analysis complete"

if __name__ == "__main__":
    main()