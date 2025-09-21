"""
Comprehensive ML Analysis Runner for Top 100 Stocks
Runs all ML models (Stock Recommender, BTST Analyzer, Options Analyzer, Sector Analyzer) 
on the top 100 stocks and generates comprehensive returns analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from realtime_ml_models import (
    RealTimeStockRecommender, 
    RealTimeBTSTAnalyzer, 
    RealTimeOptionsAnalyzer, 
    RealTimeSectorAnalyzer
)
from realtime_data_fetcher import RealTimeDataFetcher
from top100_stocks_mapping import TOP_100_STOCKS
import json
import time
from datetime import datetime
import pandas as pd
import numpy as np

class ComprehensiveMLAnalyzer:
    """Comprehensive ML Analysis Runner for Top 100 Stocks"""
    
    def __init__(self):
        # Initialize data fetcher
        self.data_fetcher = RealTimeDataFetcher()
        
        # Initialize all ML models
        self.stock_recommender = RealTimeStockRecommender(self.data_fetcher)
        self.btst_analyzer = RealTimeBTSTAnalyzer(self.data_fetcher)
        self.options_analyzer = RealTimeOptionsAnalyzer(self.data_fetcher)
        self.sector_analyzer = RealTimeSectorAnalyzer(self.data_fetcher)
        
        # Results storage
        self.results = {
            'stock_recommendations': [],
            'btst_opportunities': [],
            'options_strategies': [],
            'sector_analysis': {},
            'summary_stats': {},
            'performance_metrics': {},
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    def run_stock_recommendations(self, symbols_batch=None):
        """Run stock recommendations for specified symbols"""
        # Use top 10 stocks for testing, will scale to 100 with Fyers API in production
        symbols = symbols_batch or TOP_100_STOCKS[:10]
        
        print(f"\n📊 Running Stock Recommendations for {len(symbols)} stocks...")
        print(f"   📝 Note: Using top 10 stocks for testing. Production will use Fyers API for all 100 stocks.")
        
        recommendations = []
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"   [{i}/{len(symbols)}] Analyzing {symbol}...", end=" ")
                
                result = self.stock_recommender.predict_stock(symbol)
                if result and 'error' not in result:
                    recommendations.append({
                        'symbol': symbol,
                        'recommendation': result.get('recommendation', 'HOLD'),
                        'confidence': result.get('confidence', 0),
                        'current_price': result.get('current_price', 0),
                        'target_price': result.get('target_price', 0),
                        'potential_return': self._calculate_return(
                            result.get('current_price', 0), 
                            result.get('target_price', 0)
                        ),
                        'analysis_time': datetime.now().strftime('%H:%M:%S')
                    })
                    print(f"✅ {result.get('recommendation', 'N/A')} ({result.get('confidence', 0):.1f}%)")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown') if result else 'No result'}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)[:50]}...")
                
            time.sleep(0.05)  # Small delay to avoid overwhelming APIs
        
        self.results['stock_recommendations'] = recommendations
        return recommendations
    
    def run_btst_analysis(self, symbols_batch=None):
        """Run BTST analysis for specified symbols"""
        # Use top 5 stocks for testing BTST
        symbols = symbols_batch or TOP_100_STOCKS[:5]
        
        print(f"\n🌙 Running BTST Analysis for {len(symbols)} stocks...")
        print(f"   📝 Note: Using top 5 stocks for BTST testing. Production will use Fyers API for more stocks.")
        
        opportunities = []
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"   [{i}/{len(symbols)}] BTST {symbol}...", end=" ")
                
                result = self.btst_analyzer.analyze_btst_opportunity(symbol)
                if result and 'error' not in result:
                    btst_score = result.get('btst_score', 0)
                    if btst_score > 25:  # Only include decent opportunities
                        opportunities.append({
                            'symbol': symbol,
                            'btst_score': btst_score,
                            'recommendation': result.get('recommendation', 'AVOID'),
                            'risk_level': result.get('risk_assessment', {}).get('level', 'MEDIUM'),
                            'expected_return': result.get('expected_return', 0),
                            'analysis_time': datetime.now().strftime('%H:%M:%S')
                        })
                        print(f"✅ Score: {btst_score:.1f} ({result.get('recommendation', 'N/A')})")
                    else:
                        print(f"⚠️  Low score: {btst_score:.1f}")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown') if result else 'No result'}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)[:50]}...")
                
            time.sleep(0.05)
        
        self.results['btst_opportunities'] = opportunities
        return opportunities
    
    def run_options_analysis(self, symbols_batch=None):
        """Run options analysis for specified symbols"""
        # Use top 5 stocks for options testing
        symbols = symbols_batch or TOP_100_STOCKS[:5]
        
        print(f"\n📈 Running Options Analysis for {len(symbols)} stocks...")
        print(f"   📝 Note: Using top 5 stocks for options testing. Production will use Fyers API for more stocks.")
        
        strategies = []
        for i, symbol in enumerate(symbols, 1):
            try:
                print(f"   [{i}/{len(symbols)}] Options {symbol}...", end=" ")
                
                result = self.options_analyzer.analyze_options_opportunity(symbol)
                if result and 'error' not in result:
                    strategies.append({
                        'symbol': symbol,
                        'strategy': result.get('strategy', 'Long Call'),
                        'confidence': result.get('confidence', 0),
                        'max_profit': result.get('max_profit', 0),
                        'max_loss': result.get('max_loss', 0),
                        'breakeven': result.get('breakeven_price', 0),
                        'risk_reward_ratio': result.get('risk_reward_ratio', 0),
                        'analysis_time': datetime.now().strftime('%H:%M:%S')
                    })
                    print(f"✅ {result.get('strategy', 'N/A')} ({result.get('confidence', 0):.1f}%)")
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown') if result else 'No result'}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)[:50]}...")
                
            time.sleep(0.05)
        
        self.results['options_strategies'] = strategies
        return strategies
    
    def run_sector_analysis(self):
        """Run comprehensive sector analysis"""
        print(f"\n🏭 Running Sector Analysis...")
        
        try:
            result = self.sector_analyzer.analyze_sector_performance()
            if result:
                self.results['sector_analysis'] = result
                print(f"✅ Analyzed {len(result)} sectors successfully")
                
                # Print top performing sectors
                sector_scores = []
                for sector, data in result.items():
                    if isinstance(data, dict) and 'avg_change_percent' in data:
                        sector_scores.append((sector, data['avg_change_percent']))
                
                sector_scores.sort(key=lambda x: x[1], reverse=True)
                print("   📊 Top 3 Performing Sectors:")
                for i, (sector, change) in enumerate(sector_scores[:3], 1):
                    print(f"      {i}. {sector}: {change:+.2f}%")
                    
            else:
                print("❌ No sector analysis results")
                
        except Exception as e:
            print(f"❌ Sector analysis error: {e}")
    
    def _calculate_return(self, current_price, target_price):
        """Calculate potential return percentage"""
        if current_price and target_price and current_price > 0:
            return ((target_price - current_price) / current_price) * 100
        return 0
    
    def generate_summary_statistics(self):
        """Generate comprehensive summary statistics"""
        print(f"\n📈 Generating Summary Statistics...")
        
        stats = {
            'total_stocks_analyzed': len(self.results['stock_recommendations']),
            'total_btst_opportunities': len(self.results['btst_opportunities']),
            'total_options_strategies': len(self.results['options_strategies']),
            'sectors_analyzed': len(self.results['sector_analysis'])
        }
        
        # Stock recommendation statistics
        if self.results['stock_recommendations']:
            recommendations = self.results['stock_recommendations']
            
            buy_count = len([r for r in recommendations if r['recommendation'] in ['BUY', 'STRONG BUY']])
            sell_count = len([r for r in recommendations if r['recommendation'] in ['SELL', 'STRONG SELL']])
            hold_count = len([r for r in recommendations if r['recommendation'] == 'HOLD'])
            
            avg_confidence = np.mean([r['confidence'] for r in recommendations])
            avg_potential_return = np.mean([r['potential_return'] for r in recommendations if r['potential_return'] != 0])
            
            stats.update({
                'buy_recommendations': buy_count,
                'sell_recommendations': sell_count,
                'hold_recommendations': hold_count,
                'avg_confidence': round(avg_confidence, 2),
                'avg_potential_return': round(avg_potential_return, 2) if not np.isnan(avg_potential_return) else 0
            })
        
        # BTST statistics
        if self.results['btst_opportunities']:
            btst_ops = self.results['btst_opportunities']
            
            strong_buy_btst = len([b for b in btst_ops if b['recommendation'] == 'STRONG BUY'])
            buy_btst = len([b for b in btst_ops if b['recommendation'] == 'BUY'])
            avg_btst_score = np.mean([b['btst_score'] for b in btst_ops])
            
            stats.update({
                'strong_buy_btst': strong_buy_btst,
                'buy_btst': buy_btst,
                'avg_btst_score': round(avg_btst_score, 2)
            })
        
        # Options statistics
        if self.results['options_strategies']:
            options = self.results['options_strategies']
            
            strategy_counts = {}
            for opt in options:
                strategy = opt['strategy']
                strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            
            avg_options_confidence = np.mean([o['confidence'] for o in options])
            
            stats.update({
                'popular_strategies': dict(sorted(strategy_counts.items(), key=lambda x: x[1], reverse=True)[:3]),
                'avg_options_confidence': round(avg_options_confidence, 2)
            })
        
        self.results['summary_stats'] = stats
        return stats
    
    def generate_performance_report(self):
        """Generate detailed performance report"""
        print(f"\n📊 Generating Performance Report...")
        
        # Top performing recommendations
        stock_recs = self.results['stock_recommendations']
        if stock_recs:
            # Sort by potential return
            top_returns = sorted(
                [r for r in stock_recs if r['potential_return'] > 0], 
                key=lambda x: x['potential_return'], 
                reverse=True
            )[:10]
            
            # Sort by confidence
            high_confidence = sorted(
                stock_recs, 
                key=lambda x: x['confidence'], 
                reverse=True
            )[:10]
            
            self.results['performance_metrics'] = {
                'top_potential_returns': top_returns,
                'high_confidence_picks': high_confidence,
                'buy_recommendations_list': [r['symbol'] for r in stock_recs if r['recommendation'] in ['BUY', 'STRONG BUY']],
                'sell_recommendations_list': [r['symbol'] for r in stock_recs if r['recommendation'] in ['SELL', 'STRONG SELL']]
            }
    
    def print_comprehensive_summary(self):
        """Print comprehensive analysis summary"""
        print("\n" + "="*80)
        print("📈 COMPREHENSIVE ML ANALYSIS SUMMARY")
        print("="*80)
        
        stats = self.results['summary_stats']
        
        print(f"🎯 ANALYSIS OVERVIEW:")
        print(f"   • Total Stocks Analyzed: {stats.get('total_stocks_analyzed', 0)}")
        print(f"   • BTST Opportunities Found: {stats.get('total_btst_opportunities', 0)}")
        print(f"   • Options Strategies Generated: {stats.get('total_options_strategies', 0)}")
        print(f"   • Sectors Analyzed: {stats.get('sectors_analyzed', 0)}")
        print(f"   • Analysis Timestamp: {self.results['timestamp']}")
        
        print(f"\n📊 STOCK RECOMMENDATIONS BREAKDOWN:")
        print(f"   • BUY Recommendations: {stats.get('buy_recommendations', 0)}")
        print(f"   • SELL Recommendations: {stats.get('sell_recommendations', 0)}")
        print(f"   • HOLD Recommendations: {stats.get('hold_recommendations', 0)}")
        print(f"   • Average Confidence: {stats.get('avg_confidence', 0):.1f}%")
        print(f"   • Average Potential Return: {stats.get('avg_potential_return', 0):+.2f}%")
        
        if self.results['btst_opportunities']:
            print(f"\n🌙 BTST ANALYSIS:")
            print(f"   • Strong Buy BTST: {stats.get('strong_buy_btst', 0)}")
            print(f"   • Buy BTST: {stats.get('buy_btst', 0)}")
            print(f"   • Average BTST Score: {stats.get('avg_btst_score', 0):.1f}/100")
        
        if self.results['options_strategies']:
            print(f"\n📈 OPTIONS ANALYSIS:")
            print(f"   • Average Options Confidence: {stats.get('avg_options_confidence', 0):.1f}%")
            popular_strategies = stats.get('popular_strategies', {})
            if popular_strategies:
                print(f"   • Popular Strategies:")
                for strategy, count in popular_strategies.items():
                    print(f"     - {strategy}: {count} occurrences")
        
        # Top performers
        perf_metrics = self.results.get('performance_metrics', {})
        
        if perf_metrics.get('top_potential_returns'):
            print(f"\n🏆 TOP 5 POTENTIAL RETURNS:")
            for i, stock in enumerate(perf_metrics['top_potential_returns'][:5], 1):
                print(f"   {i}. {stock['symbol']}: {stock['potential_return']:+.2f}% "
                      f"({stock['recommendation']}, Confidence: {stock['confidence']:.1f}%)")
        
        if perf_metrics.get('buy_recommendations_list'):
            buy_list = perf_metrics['buy_recommendations_list']
            print(f"\n💰 BUY RECOMMENDATIONS ({len(buy_list)} stocks):")
            print(f"   {', '.join(buy_list[:15])}{'...' if len(buy_list) > 15 else ''}")
        
        if perf_metrics.get('sell_recommendations_list'):
            sell_list = perf_metrics['sell_recommendations_list']
            print(f"\n📉 SELL RECOMMENDATIONS ({len(sell_list)} stocks):")
            print(f"   {', '.join(sell_list[:10])}{'...' if len(sell_list) > 10 else ''}")
        
        # Sector performance
        if self.results['sector_analysis']:
            print(f"\n🏭 SECTOR PERFORMANCE:")
            sector_data = []
            for sector, data in self.results['sector_analysis'].items():
                if isinstance(data, dict) and 'avg_change_percent' in data:
                    sector_data.append((sector, data['avg_change_percent'], data.get('recommendation', 'N/A')))
            
            sector_data.sort(key=lambda x: x[1], reverse=True)
            for i, (sector, change, rec) in enumerate(sector_data[:5], 1):
                print(f"   {i}. {sector}: {change:+.2f}% ({rec})")
        
        print("\n" + "="*80)
    
    def save_results(self, filename=None):
        """Save all results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'comprehensive_ml_analysis_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"💾 Results saved to: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
            return None

def main():
    """Main execution function"""
    print("🚀 COMPREHENSIVE ML ANALYSIS - TESTING VERSION (TOP 10 STOCKS)")
    print("="*60)
    print("Running all ML models on top 10 stocks for testing...")
    print("📝 Production version will use Fyers API for all 100 stocks.")
    print("")
    
    # Initialize analyzer
    analyzer = ComprehensiveMLAnalyzer()
    
    start_time = time.time()
    
    try:
        # Run all analyses
        analyzer.run_stock_recommendations(TOP_100_STOCKS[:10])  # Top 10 for testing
        analyzer.run_btst_analysis(TOP_100_STOCKS[:5])           # Top 5 for BTST testing
        analyzer.run_options_analysis(TOP_100_STOCKS[:5])        # Top 5 for options testing
        analyzer.run_sector_analysis()
        
        # Generate statistics and reports
        analyzer.generate_summary_statistics()
        analyzer.generate_performance_report()
        
        # Print comprehensive summary
        analyzer.print_comprehensive_summary()
        
        # Save results
        filename = analyzer.save_results()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n⏱️  Total Analysis Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"🎉 COMPREHENSIVE ANALYSIS COMPLETE!")
        
        return analyzer.results
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Analysis interrupted by user")
        return None
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    results = main()
