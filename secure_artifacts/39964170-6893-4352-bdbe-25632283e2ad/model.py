import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RelativeStrengthRotation:
    def __init__(self, symbols):
        self.symbols = symbols
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=60)  # 2 months data for short-term analysis
        
    def download_data(self):
        """Download historical price data for all symbols"""
        print("Downloading stock data...")
        data = yf.download(self.symbols, start=self.start_date, end=self.end_date)['Close']
        return data
    
    def calculate_relative_strength(self, prices):
        """Calculate relative strength metrics"""
        # Calculate returns
        returns_1d = prices.pct_change().iloc[-1]  # 1-day return
        returns_5d = prices.pct_change(5).iloc[-1]  # 5-day return
        returns_20d = prices.pct_change(20).iloc[-1]  # 20-day return
        
        # Calculate momentum indicators
        sma_20 = prices.rolling(window=20).mean().iloc[-1]
        price_vs_sma_20 = (prices.iloc[-1] / sma_20 - 1) * 100
        
        # Calculate RSI (14-day)
        def calculate_rsi(series, period=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.iloc[-1]
        
        rsi_values = {}
        for symbol in self.symbols:
            rsi_values[symbol] = calculate_rsi(prices[symbol])
        
        # Create results dataframe
        results = pd.DataFrame({
            'Symbol': self.symbols,
            'Last_Price': prices.iloc[-1].values,
            '1D_Return_%': returns_1d.values * 100,
            '5D_Return_%': returns_5d.values * 100,
            '20D_Return_%': returns_20d.values * 100,
            'Price_vs_SMA20_%': price_vs_sma_20.values,
            'RSI_14': list(rsi_values.values())
        })
        
        return results
    
    def calculate_composite_score(self, results):
        """Calculate composite relative strength score"""
        # Normalize each metric (0-100 scale)
        metrics = ['1D_Return_%', '5D_Return_%', '20D_Return_%', 'Price_vs_SMA20_%']
        
        for metric in metrics:
            results[f'{metric}_Score'] = self._normalize_score(results[metric])
        
        # RSI scoring (higher is better but avoid extremes)
        results['RSI_Score'] = results['RSI_14'].apply(
            lambda x: 100 if 60 <= x <= 80 else 
                    80 if 50 <= x < 60 or 80 < x <= 70 else 
                    60 if 40 <= x < 50 or 70 < x <= 85 else 
                    40 if 30 <= x < 40 or 85 < x <= 90 else 20
        )
        
        # Calculate composite score (weighted average)
        weights = {
            '1D_Return_%_Score': 0.15,
            '5D_Return_%_Score': 0.25,
            '20D_Return_%_Score': 0.30,
            'Price_vs_SMA20_%_Score': 0.20,
            'RSI_Score': 0.10
        }
        
        results['Composite_Score'] = (
            results['1D_Return_%_Score'] * weights['1D_Return_%_Score'] +
            results['5D_Return_%_Score'] * weights['5D_Return_%_Score'] +
            results['20D_Return_%_Score'] * weights['20D_Return_%_Score'] +
            results['Price_vs_SMA20_%_Score'] * weights['Price_vs_SMA20_%_Score'] +
            results['RSI_Score'] * weights['RSI_Score']
        )
        
        return results
    
    def _normalize_score(self, series):
        """Normalize series to 0-100 scale"""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return 50  # Neutral score if all values are same
        return ((series - min_val) / (max_val - min_val)) * 100
    
    def generate_rotation_signal(self, results):
        """Generate rotation signals based on composite score"""
        results = results.sort_values('Composite_Score', ascending=False)
        
        # Assign rotation ranks and signals
        results['Rank'] = range(1, len(results) + 1)
        
        # Signal classification
        conditions = [
            results['Composite_Score'] >= 80,
            results['Composite_Score'] >= 60,
            results['Composite_Score'] >= 40,
            results['Composite_Score'] >= 20,
            results['Composite_Score'] < 20
        ]
        
        choices = ['Strong Buy', 'Buy', 'Neutral', 'Weak', 'Avoid']
        
        results['Signal'] = np.select(conditions, choices, default='Neutral')
        
        return results
    
    def run_analysis(self):
        """Run complete relative strength rotation analysis"""
        try:
            # Download data
            price_data = self.download_data()
            
            if price_data.empty:
                print("No data downloaded. Please check your internet connection and symbols.")
                return None
            
            # Calculate relative strength
            results = self.calculate_relative_strength(price_data)
            
            # Calculate composite score
            results = self.calculate_composite_score(results)
            
            # Generate rotation signals
            final_results = self.generate_rotation_signal(results)
            
            return final_results
            
        except Exception as e:
            print(f"Error in analysis: {e}")
            return None

def main():
    # List of Nifty 50 stocks
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
    
    print("Short-Term Relative Strength Rotation Analysis")
    print("=" * 70)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Number of Stocks: {len(symbols)}")
    print("=" * 70)
    
    # Initialize and run analysis
    analyzer = RelativeStrengthRotation(symbols)
    results = analyzer.run_analysis()
    
    if results is not None:
        # Display top 10 and bottom 10 performers
        print("\nTOP 10 STRONGEST STOCKS:")
        print("=" * 120)
        top_10 = results.head(10)[['Rank', 'Symbol', 'Last_Price', 'Composite_Score', 
                                 '1D_Return_%', '5D_Return_%', '20D_Return_%', 'Signal']]
        print(top_10.to_string(index=False))
        
        print("\n" + "=" * 120)
        print("BOTTOM 10 WEAKEST STOCKS:")
        print("=" * 120)
        bottom_10 = results.tail(10)[['Rank', 'Symbol', 'Last_Price', 'Composite_Score', 
                                    '1D_Return_%', '5D_Return_%', '20D_Return_%', 'Signal']]
        print(bottom_10.to_string(index=False))
        
        # Display summary statistics
        print("\n" + "=" * 120)
        print("SUMMARY STATISTICS:")
        print("=" * 120)
        print(f"Average Composite Score: {results['Composite_Score'].mean():.2f}")
        print(f"Highest Composite Score: {results['Composite_Score'].max():.2f}")
        print(f"Lowest Composite Score: {results['Composite_Score'].min():.2f}")
        
        # Count signals
        signal_counts = results['Signal'].value_counts()
        print("\nSignal Distribution:")
        for signal, count in signal_counts.items():
            print(f"{signal}: {count} stocks")
        
        # Save results to CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relative_strength_rotation_{timestamp}.csv"
        results.to_csv(filename, index=False)
        print(f"\nResults saved to: {filename}")
        
    else:
        print("Analysis failed. Please check your inputs and try again.")

if __name__ == "__main__":
    main()