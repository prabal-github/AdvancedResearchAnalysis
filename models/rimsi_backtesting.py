"""
RIMSI Backtesting & Model Execution Engine
Advanced backtesting system with multiple engine support
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Backtesting frameworks
try:
    import backtrader as bt
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False

try:
    import vectorbt as vbt
    VECTORBT_AVAILABLE = True
except ImportError:
    VECTORBT_AVAILABLE = False

try:
    import zipline
    from zipline.api import order_optimal_portfolio, record, symbol
    from zipline.utils.factory import create_simulation_parameters
    ZIPLINE_AVAILABLE = True
except ImportError:
    ZIPLINE_AVAILABLE = False

# Risk and portfolio optimization
try:
    import empyrical
    EMPYRICAL_AVAILABLE = True
except ImportError:
    EMPYRICAL_AVAILABLE = False

try:
    from pypfopt import risk_models, expected_returns, EfficientFrontier
    from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
    PYPFOPT_AVAILABLE = True
except ImportError:
    PYPFOPT_AVAILABLE = False

class RIMSIBacktester:
    """
    Advanced backtesting engine with multiple framework support
    """
    
    def __init__(self, engine='auto'):
        """
        Initialize backtester
        
        Args:
            engine: 'backtrader', 'vectorbt', 'zipline', or 'auto' for best available
        """
        self.engine = engine
        self.available_engines = self._detect_engines()
        self.selected_engine = self._select_engine(engine)
        
    def _detect_engines(self) -> Dict[str, bool]:
        """Detect available backtesting engines"""
        return {
            'backtrader': BACKTRADER_AVAILABLE,
            'vectorbt': VECTORBT_AVAILABLE,
            'zipline': ZIPLINE_AVAILABLE,
            'native': True  # Always available
        }
    
    def _select_engine(self, preference: str) -> str:
        """Select the best available engine"""
        if preference == 'auto':
            # Priority order for automatic selection
            for engine in ['vectorbt', 'backtrader', 'zipline', 'native']:
                if self.available_engines.get(engine, False):
                    return engine
        elif preference in self.available_engines and self.available_engines[preference]:
            return preference
        
        return 'native'  # Fallback
    
    async def run_strategy(self, strategy_code: str, config: Dict) -> Dict:
        """
        Run strategy backtest with specified configuration
        
        Args:
            strategy_code: Python strategy code
            config: Backtest configuration
        """
        try:
            if self.selected_engine == 'vectorbt':
                return await self._run_vectorbt_backtest(strategy_code, config)
            elif self.selected_engine == 'backtrader':
                return await self._run_backtrader_backtest(strategy_code, config)
            elif self.selected_engine == 'zipline':
                return await self._run_zipline_backtest(strategy_code, config)
            else:
                return await self._run_native_backtest(strategy_code, config)
        except Exception as e:
            return {
                'error': f'Backtesting failed: {str(e)}',
                'engine_used': self.selected_engine
            }
    
    async def _run_vectorbt_backtest(self, strategy_code: str, config: Dict) -> Dict:
        """Run backtest using vectorbt (fast, vectorized)"""
        
        try:
            # Get data
            data = self._get_market_data(config)
            
            # Parse strategy for vectorbt signals
            signals = self._parse_strategy_signals(strategy_code, data, config)
            
            # Create portfolio
            portfolio = vbt.Portfolio.from_signals(
                data['Close'],
                signals['entries'],
                signals['exits'],
                init_cash=config.get('initial_capital', 100000),
                fees=config.get('commission', 0.001),
                freq='D'
            )
            
            # Calculate metrics
            results = {
                'engine': 'vectorbt',
                'total_return': portfolio.total_return(),
                'annualized_return': portfolio.annualized_return(),
                'sharpe_ratio': portfolio.sharpe_ratio(),
                'max_drawdown': portfolio.max_drawdown(),
                'win_rate': portfolio.win_rate(),
                'profit_factor': portfolio.profit_factor(),
                'total_trades': portfolio.total_trades(),
                'final_value': portfolio.final_value(),
                'calmar_ratio': portfolio.calmar_ratio(),
                'sortino_ratio': portfolio.sortino_ratio(),
                'volatility': portfolio.returns().std() * np.sqrt(252),
                'var_95': portfolio.returns().quantile(0.05),
                'trades': portfolio.trades.records_readable.to_dict('records') if hasattr(portfolio.trades, 'records_readable') else []
            }
            
            return results
            
        except Exception as e:
            return {'error': f'VectorBT backtest failed: {str(e)}'}
    
    async def _run_backtrader_backtest(self, strategy_code: str, config: Dict) -> Dict:
        """Run backtest using Backtrader (flexible)"""
        
        try:
            # Create Backtrader cerebro engine
            cerebro = bt.Cerebro()
            
            # Get data
            data = self._get_market_data(config)
            
            # Convert to Backtrader format
            bt_data = bt.feeds.PandasData(dataname=data)
            cerebro.adddata(bt_data)
            
            # Create dynamic strategy class from code
            strategy_class = self._create_backtrader_strategy(strategy_code, config)
            cerebro.addstrategy(strategy_class)
            
            # Set initial capital
            initial_cash = config.get('initial_capital', 100000)
            cerebro.broker.setcash(initial_cash)
            
            # Set commission
            cerebro.broker.setcommission(commission=config.get('commission', 0.001))
            
            # Add analyzers
            cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
            cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
            cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
            
            # Run backtest
            results = cerebro.run()
            final_value = cerebro.broker.getvalue()
            
            # Extract results
            strat = results[0]
            
            return {
                'engine': 'backtrader',
                'total_return': (final_value - initial_cash) / initial_cash,
                'annualized_return': strat.analyzers.returns.get_analysis().get('ravg', 0) * 252,
                'sharpe_ratio': strat.analyzers.sharpe.get_analysis().get('sharperatio', 0),
                'max_drawdown': strat.analyzers.drawdown.get_analysis().get('max', {}).get('drawdown', 0) / 100,
                'final_value': final_value,
                'initial_capital': initial_cash,
                'trade_analysis': strat.analyzers.trades.get_analysis()
            }
            
        except Exception as e:
            return {'error': f'Backtrader backtest failed: {str(e)}'}
    
    async def _run_zipline_backtest(self, strategy_code: str, config: Dict) -> Dict:
        """Run backtest using Zipline (institutional-grade)"""
        
        try:
            # Note: Zipline requires more setup for data bundles
            # This is a simplified implementation
            return {'error': 'Zipline integration requires additional setup for data bundles'}
            
        except Exception as e:
            return {'error': f'Zipline backtest failed: {str(e)}'}
    
    async def _run_native_backtest(self, strategy_code: str, config: Dict) -> Dict:
        """Run backtest using native implementation"""
        
        try:
            # Get market data
            data = self._get_market_data(config)
            
            # Initialize portfolio
            initial_capital = config.get('initial_capital', 100000)
            cash = initial_capital
            position = 0
            portfolio_values = []
            trades = []
            
            # Parse strategy signals
            signals = self._parse_strategy_signals_native(strategy_code, data, config)
            
            # Simulate trading
            for i in range(len(data)):
                price = data['Close'].iloc[i]
                date = data.index[i]
                
                # Check for entry signal
                if signals['entries'].iloc[i] and position == 0:
                    # Buy signal
                    shares_to_buy = int(cash * 0.95 / price)  # Use 95% of cash
                    if shares_to_buy > 0:
                        position = shares_to_buy
                        cash -= shares_to_buy * price * (1 + config.get('commission', 0.001))
                        trades.append({
                            'date': date,
                            'action': 'BUY',
                            'price': price,
                            'shares': shares_to_buy,
                            'value': shares_to_buy * price
                        })
                
                # Check for exit signal
                elif signals['exits'].iloc[i] and position > 0:
                    # Sell signal
                    cash += position * price * (1 - config.get('commission', 0.001))
                    trades.append({
                        'date': date,
                        'action': 'SELL',
                        'price': price,
                        'shares': position,
                        'value': position * price
                    })
                    position = 0
                
                # Calculate portfolio value
                portfolio_value = cash + position * price
                portfolio_values.append(portfolio_value)
            
            # Calculate returns
            portfolio_series = pd.Series(portfolio_values, index=data.index)
            returns = portfolio_series.pct_change().dropna()
            
            # Calculate metrics
            total_return = (portfolio_values[-1] - initial_capital) / initial_capital
            annualized_return = (1 + total_return) ** (252 / len(returns)) - 1
            volatility = returns.std() * np.sqrt(252)
            sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
            
            # Calculate drawdown
            cumulative = portfolio_series / portfolio_series.cummax()
            max_drawdown = (cumulative - 1).min()
            
            # Calculate win rate
            winning_trades = [t for t in trades[1::2] if len(trades) > 1]  # Sell trades
            if len(winning_trades) > 0 and len(trades) > 1:
                profitable_trades = 0
                for i in range(0, len(trades) - 1, 2):
                    if i + 1 < len(trades):
                        buy_price = trades[i]['price']
                        sell_price = trades[i + 1]['price']
                        if sell_price > buy_price:
                            profitable_trades += 1
                win_rate = profitable_trades / (len(trades) // 2)
            else:
                win_rate = 0
            
            return {
                'engine': 'native',
                'total_return': total_return,
                'annualized_return': annualized_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'volatility': volatility,
                'win_rate': win_rate,
                'total_trades': len(trades),
                'final_value': portfolio_values[-1],
                'initial_capital': initial_capital,
                'trades': trades,
                'portfolio_values': portfolio_values,
                'var_95': returns.quantile(0.05) if len(returns) > 0 else 0
            }
            
        except Exception as e:
            return {'error': f'Native backtest failed: {str(e)}'}
    
    def _get_market_data(self, config: Dict) -> pd.DataFrame:
        """Get market data for backtesting"""
        
        symbol = config.get('symbol', 'SPY')
        start_date = config.get('start_date', '2022-01-01')
        end_date = config.get('end_date', '2023-12-31')
        
        # Download data
        data = yf.download(symbol, start=start_date, end=end_date)
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Ensure we have required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return data
    
    def _parse_strategy_signals(self, strategy_code: str, data: pd.DataFrame, config: Dict) -> Dict:
        """Parse strategy code to extract buy/sell signals for vectorbt"""
        
        # This is a simplified signal parser
        # In production, you'd want more sophisticated code analysis
        
        # Create default signals (buy and hold)
        entries = pd.Series(False, index=data.index)
        exits = pd.Series(False, index=data.index)
        
        # Set first day as entry, last day as exit
        entries.iloc[0] = True
        exits.iloc[-1] = True
        
        # Look for common strategy patterns in code
        if 'moving average' in strategy_code.lower() or 'sma' in strategy_code.lower():
            # Moving average crossover strategy
            short_window = 20
            long_window = 50
            
            data['SMA_short'] = data['Close'].rolling(window=short_window).mean()
            data['SMA_long'] = data['Close'].rolling(window=long_window).mean()
            
            entries = (data['SMA_short'] > data['SMA_long']) & (data['SMA_short'].shift(1) <= data['SMA_long'].shift(1))
            exits = (data['SMA_short'] < data['SMA_long']) & (data['SMA_short'].shift(1) >= data['SMA_long'].shift(1))
        
        elif 'rsi' in strategy_code.lower():
            # RSI strategy
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            entries = (rsi < 30) & (rsi.shift(1) >= 30)  # Oversold
            exits = (rsi > 70) & (rsi.shift(1) <= 70)    # Overbought
        
        return {'entries': entries, 'exits': exits}
    
    def _parse_strategy_signals_native(self, strategy_code: str, data: pd.DataFrame, config: Dict) -> Dict:
        """Parse strategy code for native backtester"""
        return self._parse_strategy_signals(strategy_code, data, config)
    
    def _create_backtrader_strategy(self, strategy_code: str, config: Dict):
        """Create Backtrader strategy class from code"""
        
        class DynamicStrategy(bt.Strategy):
            def __init__(self):
                self.dataclose = self.datas[0].close
                
                # Add indicators based on strategy code
                if 'moving average' in strategy_code.lower() or 'sma' in strategy_code.lower():
                    self.sma_short = bt.indicators.SimpleMovingAverage(
                        self.datas[0], period=20)
                    self.sma_long = bt.indicators.SimpleMovingAverage(
                        self.datas[0], period=50)
                
                elif 'rsi' in strategy_code.lower():
                    self.rsi = bt.indicators.RSI_SMA(self.datas[0], period=14)
            
            def next(self):
                if not self.position:
                    # Entry logic
                    if hasattr(self, 'sma_short') and hasattr(self, 'sma_long'):
                        if self.sma_short[0] > self.sma_long[0]:
                            self.buy()
                    elif hasattr(self, 'rsi'):
                        if self.rsi[0] < 30:
                            self.buy()
                else:
                    # Exit logic
                    if hasattr(self, 'sma_short') and hasattr(self, 'sma_long'):
                        if self.sma_short[0] < self.sma_long[0]:
                            self.sell()
                    elif hasattr(self, 'rsi'):
                        if self.rsi[0] > 70:
                            self.sell()
        
        return DynamicStrategy


class RIMSIRiskAssessment:
    """
    Advanced risk assessment and compliance checking
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'max_drawdown': -0.20,      # Maximum 20% drawdown
            'sharpe_ratio': 1.0,        # Minimum Sharpe ratio
            'var_95': -0.05,            # Maximum 5% daily VaR
            'volatility': 0.30,         # Maximum 30% annual volatility
            'leverage': 2.0,            # Maximum 2x leverage
        }
    
    def assess_strategy_risk(self, backtest_results: Dict, strategy_code: str) -> Dict:
        """
        Comprehensive risk assessment of strategy
        """
        
        risk_assessment = {
            'overall_risk_score': 0,
            'risk_level': 'Unknown',
            'warnings': [],
            'violations': [],
            'recommendations': [],
            'compliance_score': 100,
            'metrics_analysis': {}
        }
        
        # Analyze backtest metrics
        if 'error' not in backtest_results:
            risk_assessment['metrics_analysis'] = self._analyze_performance_metrics(backtest_results)
            
            # Check risk thresholds
            violations = self._check_risk_thresholds(backtest_results)
            risk_assessment['violations'].extend(violations)
            
            # Calculate overall risk score
            risk_assessment['overall_risk_score'] = self._calculate_risk_score(backtest_results)
            risk_assessment['risk_level'] = self._determine_risk_level(risk_assessment['overall_risk_score'])
        
        # Analyze strategy code for risks
        code_risks = self._analyze_strategy_code(strategy_code)
        risk_assessment['warnings'].extend(code_risks['warnings'])
        risk_assessment['violations'].extend(code_risks['violations'])
        
        # Generate recommendations
        risk_assessment['recommendations'] = self._generate_risk_recommendations(
            risk_assessment, backtest_results, strategy_code
        )
        
        # Calculate compliance score
        risk_assessment['compliance_score'] = max(0, 100 - len(risk_assessment['violations']) * 20 - len(risk_assessment['warnings']) * 5)
        
        return risk_assessment
    
    def _analyze_performance_metrics(self, results: Dict) -> Dict:
        """Analyze performance metrics for risk factors"""
        
        analysis = {}
        
        # Sharpe ratio analysis
        sharpe = results.get('sharpe_ratio', 0)
        if sharpe > 2:
            analysis['sharpe_assessment'] = 'Excellent risk-adjusted returns'
        elif sharpe > 1:
            analysis['sharpe_assessment'] = 'Good risk-adjusted returns'
        elif sharpe > 0:
            analysis['sharpe_assessment'] = 'Moderate risk-adjusted returns'
        else:
            analysis['sharpe_assessment'] = 'Poor risk-adjusted returns'
        
        # Drawdown analysis
        max_dd = results.get('max_drawdown', 0)
        if max_dd > -0.1:
            analysis['drawdown_assessment'] = 'Low drawdown - excellent risk control'
        elif max_dd > -0.2:
            analysis['drawdown_assessment'] = 'Moderate drawdown - acceptable risk'
        else:
            analysis['drawdown_assessment'] = 'High drawdown - review risk management'
        
        # Volatility analysis
        volatility = results.get('volatility', 0)
        if volatility < 0.15:
            analysis['volatility_assessment'] = 'Low volatility - conservative strategy'
        elif volatility < 0.25:
            analysis['volatility_assessment'] = 'Moderate volatility - balanced approach'
        else:
            analysis['volatility_assessment'] = 'High volatility - aggressive strategy'
        
        return analysis
    
    def _check_risk_thresholds(self, results: Dict) -> List[str]:
        """Check if results violate risk thresholds"""
        
        violations = []
        
        # Check maximum drawdown
        max_dd = results.get('max_drawdown', 0)
        if max_dd < self.risk_thresholds['max_drawdown']:
            violations.append(f"Maximum drawdown {max_dd:.2%} exceeds threshold {self.risk_thresholds['max_drawdown']:.2%}")
        
        # Check Sharpe ratio
        sharpe = results.get('sharpe_ratio', 0)
        if sharpe < self.risk_thresholds['sharpe_ratio']:
            violations.append(f"Sharpe ratio {sharpe:.2f} below minimum threshold {self.risk_thresholds['sharpe_ratio']:.2f}")
        
        # Check VaR
        var_95 = results.get('var_95', 0)
        if var_95 < self.risk_thresholds['var_95']:
            violations.append(f"VaR 95% {var_95:.2%} exceeds risk threshold {self.risk_thresholds['var_95']:.2%}")
        
        # Check volatility
        volatility = results.get('volatility', 0)
        if volatility > self.risk_thresholds['volatility']:
            violations.append(f"Volatility {volatility:.2%} exceeds maximum threshold {self.risk_thresholds['volatility']:.2%}")
        
        return violations
    
    def _calculate_risk_score(self, results: Dict) -> int:
        """Calculate overall risk score (0-100, higher = more risky)"""
        
        score = 0
        
        # Drawdown contribution (0-40 points)
        max_dd = abs(results.get('max_drawdown', 0))
        score += min(40, max_dd * 200)
        
        # Volatility contribution (0-30 points)
        volatility = results.get('volatility', 0)
        score += min(30, volatility * 100)
        
        # Sharpe ratio contribution (0-30 points, inverted)
        sharpe = results.get('sharpe_ratio', 0)
        if sharpe <= 0:
            score += 30
        elif sharpe < 1:
            score += 30 * (1 - sharpe)
        # No penalty for Sharpe > 1
        
        return min(100, int(score))
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level from score"""
        
        if risk_score <= 30:
            return 'Low'
        elif risk_score <= 60:
            return 'Medium'
        else:
            return 'High'
    
    def _analyze_strategy_code(self, strategy_code: str) -> Dict:
        """Analyze strategy code for potential risks"""
        
        warnings = []
        violations = []
        
        code_lower = strategy_code.lower()
        
        # Check for high-frequency patterns
        if any(term in code_lower for term in ['sleep(0', 'time.sleep(0', 'millisecond', 'microsecond']):
            warnings.append('High-frequency trading patterns detected - may require special compliance')
        
        # Check for leverage usage
        if any(term in code_lower for term in ['leverage', 'margin', 'borrowed']):
            warnings.append('Leverage usage detected - increases risk exposure')
        
        # Check for stop-loss
        if not any(term in code_lower for term in ['stop', 'loss', 'exit']):
            warnings.append('No apparent stop-loss or exit strategy detected')
        
        # Check for position sizing
        if not any(term in code_lower for term in ['size', 'amount', 'quantity', 'shares']):
            warnings.append('No explicit position sizing detected')
        
        # Check for market manipulation patterns
        if any(term in code_lower for term in ['pump', 'dump', 'manipulat', 'corner']):
            violations.append('Potential market manipulation patterns detected')
        
        # Check for wash trading patterns
        if 'wash' in code_lower and 'trad' in code_lower:
            violations.append('Potential wash trading patterns detected')
        
        return {'warnings': warnings, 'violations': violations}
    
    def _generate_risk_recommendations(self, risk_assessment: Dict, results: Dict, strategy_code: str) -> List[str]:
        """Generate risk management recommendations"""
        
        recommendations = []
        
        # Based on risk level
        if risk_assessment['risk_level'] == 'High':
            recommendations.append('Consider reducing position sizes due to high risk level')
            recommendations.append('Implement stricter stop-loss rules')
            recommendations.append('Add position sizing based on volatility')
        
        # Based on specific metrics
        if results.get('max_drawdown', 0) < -0.15:
            recommendations.append('Implement dynamic position sizing to reduce drawdowns')
        
        if results.get('sharpe_ratio', 0) < 1.0:
            recommendations.append('Optimize entry/exit rules to improve risk-adjusted returns')
        
        if results.get('volatility', 0) > 0.25:
            recommendations.append('Consider volatility-based position sizing')
        
        # Based on code analysis
        if 'stop' not in strategy_code.lower():
            recommendations.append('Add stop-loss risk management to the strategy')
        
        if 'position' not in strategy_code.lower():
            recommendations.append('Implement proper position sizing rules')
        
        # General recommendations
        recommendations.append('Monitor strategy performance in paper trading before live deployment')
        recommendations.append('Set up real-time risk monitoring and alerts')
        
        return list(set(recommendations))  # Remove duplicates


class RIMSIDataProvider:
    """
    Multi-source data provider for backtesting
    """
    
    def __init__(self):
        self.data_sources = {
            'yfinance': True,  # Always available
            'alpha_vantage': False,
            'polygon': False,
            'alpaca': False
        }
        
        # Check for additional data sources
        self._detect_data_sources()
    
    def _detect_data_sources(self):
        """Detect available data sources"""
        
        try:
            import alpha_vantage
            self.data_sources['alpha_vantage'] = True
        except ImportError:
            pass
        
        try:
            import polygon
            self.data_sources['polygon'] = True
        except ImportError:
            pass
        
        try:
            import alpaca_trade_api
            self.data_sources['alpaca'] = True
        except ImportError:
            pass
    
    def get_data(self, symbol: str, start_date: str, end_date: str, source: str = 'auto') -> pd.DataFrame:
        """
        Get market data from specified source
        """
        
        if source == 'auto':
            source = 'yfinance'  # Default to yfinance
        
        if source == 'yfinance':
            return self._get_yfinance_data(symbol, start_date, end_date)
        else:
            # Fallback to yfinance
            return self._get_yfinance_data(symbol, start_date, end_date)
    
    def _get_yfinance_data(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Get data from Yahoo Finance"""
        
        try:
            data = yf.download(symbol, start=start_date, end=end_date, progress=False)
            if data.empty:
                raise ValueError(f"No data available for {symbol}")
            return data
        except Exception as e:
            raise ValueError(f"Failed to get data for {symbol}: {str(e)}")
    
    def get_multiple_assets(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """Get data for multiple assets"""
        
        data_dict = {}
        for symbol in symbols:
            try:
                data_dict[symbol] = self.get_data(symbol, start_date, end_date)
            except Exception as e:
                print(f"Failed to get data for {symbol}: {e}")
        
        return data_dict


# Global instances
_rimsi_backtester = None
_rimsi_risk_assessor = None
_rimsi_data_provider = None

def get_rimsi_backtester(engine='auto'):
    """Get global backtester instance"""
    global _rimsi_backtester
    if _rimsi_backtester is None:
        _rimsi_backtester = RIMSIBacktester(engine)
    return _rimsi_backtester

def get_rimsi_risk_assessor():
    """Get global risk assessor instance"""
    global _rimsi_risk_assessor
    if _rimsi_risk_assessor is None:
        _rimsi_risk_assessor = RIMSIRiskAssessment()
    return _rimsi_risk_assessor

def get_rimsi_data_provider():
    """Get global data provider instance"""
    global _rimsi_data_provider
    if _rimsi_data_provider is None:
        _rimsi_data_provider = RIMSIDataProvider()
    return _rimsi_data_provider
