"""
RIMSI Portfolio Optimization & Risk Models
Advanced portfolio optimization with multiple methodologies
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Portfolio optimization
try:
    from pypfopt import risk_models, expected_returns, EfficientFrontier
    from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
    from pypfopt.objective_functions import L2_reg
    PYPFOPT_AVAILABLE = True
except ImportError:
    PYPFOPT_AVAILABLE = False

# Risk metrics
try:
    import empyrical
    EMPYRICAL_AVAILABLE = True
except ImportError:
    EMPYRICAL_AVAILABLE = False

# Advanced optimization
try:
    from scipy.optimize import minimize
    from scipy import linalg
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# Machine learning for factor models
try:
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LinearRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class RIMSIPortfolioOptimizer:
    """
    Advanced portfolio optimization with multiple methodologies
    """
    
    def __init__(self):
        self.available_methods = self._detect_methods()
        
    def _detect_methods(self) -> Dict[str, bool]:
        """Detect available optimization methods"""
        return {
            'pypfopt': PYPFOPT_AVAILABLE,
            'empyrical': EMPYRICAL_AVAILABLE,
            'scipy': SCIPY_AVAILABLE,
            'sklearn': SKLEARN_AVAILABLE,
            'native': True
        }
    
    async def optimize_portfolio(self, symbols: List[str], method: str = 'auto', 
                               objective: str = 'sharpe', constraints: Dict = None) -> Dict:
        """
        Optimize portfolio using specified method and objective
        
        Args:
            symbols: List of asset symbols
            method: Optimization method ('pypfopt', 'native', 'auto')
            objective: Optimization objective ('sharpe', 'volatility', 'return')
            constraints: Additional constraints
        """
        
        try:
            # Get data
            data = await self._get_portfolio_data(symbols)
            
            if method == 'auto':
                method = 'pypfopt' if PYPFOPT_AVAILABLE else 'native'
            
            # Run optimization
            if method == 'pypfopt' and PYPFOPT_AVAILABLE:
                return await self._optimize_pypfopt(data, objective, constraints)
            else:
                return await self._optimize_native(data, objective, constraints)
                
        except Exception as e:
            return {'error': f'Portfolio optimization failed: {str(e)}'}
    
    async def _get_portfolio_data(self, symbols: List[str], period: str = '2y') -> pd.DataFrame:
        """Get historical data for portfolio assets"""
        
        try:
            # Download data for all symbols
            data = yf.download(symbols, period=period, progress=False)['Close']
            
            if isinstance(data, pd.Series):
                # Single asset case
                data = data.to_frame(symbols[0])
            
            # Remove any symbols with insufficient data
            data = data.dropna(axis=1, thresh=len(data) * 0.7)  # Require 70% data availability
            
            if data.empty:
                raise ValueError("No valid data for portfolio optimization")
            
            return data
            
        except Exception as e:
            raise ValueError(f"Failed to get portfolio data: {str(e)}")
    
    async def _optimize_pypfopt(self, data: pd.DataFrame, objective: str, constraints: Dict = None) -> Dict:
        """Optimize using PyPortfolioOpt library"""
        
        try:
            # Calculate expected returns and risk model
            returns = expected_returns.mean_historical_return(data)
            cov_matrix = risk_models.sample_cov(data)
            
            # Create efficient frontier
            ef = EfficientFrontier(returns, cov_matrix)
            
            # Add constraints
            if constraints:
                if 'max_weight' in constraints:
                    ef.add_constraint(lambda w: w <= constraints['max_weight'])
                if 'min_weight' in constraints:
                    ef.add_constraint(lambda w: w >= constraints['min_weight'])
                if 'sectors' in constraints:
                    # Sector constraints would need additional implementation
                    pass
            
            # Optimize based on objective
            if objective == 'sharpe':
                weights = ef.max_sharpe(risk_free_rate=0.02)
            elif objective == 'volatility':
                weights = ef.min_volatility()
            elif objective == 'return':
                target_return = constraints.get('target_return', 0.15) if constraints else 0.15
                weights = ef.efficient_return(target_return)
            else:
                weights = ef.max_sharpe()
            
            # Clean weights
            cleaned_weights = ef.clean_weights()
            
            # Calculate portfolio performance
            performance = ef.portfolio_performance(risk_free_rate=0.02)
            
            # Discrete allocation
            latest_prices = get_latest_prices(data)
            total_value = constraints.get('total_value', 100000) if constraints else 100000
            
            da = DiscreteAllocation(cleaned_weights, latest_prices, total_portfolio_value=total_value)
            allocation, leftover = da.greedy_portfolio()
            
            return {
                'method': 'pypfopt',
                'objective': objective,
                'weights': dict(cleaned_weights),
                'expected_return': performance[0],
                'volatility': performance[1],
                'sharpe_ratio': performance[2],
                'allocation': allocation,
                'leftover_cash': leftover,
                'total_value': total_value
            }
            
        except Exception as e:
            return {'error': f'PyPortfolioOpt optimization failed: {str(e)}'}
    
    async def _optimize_native(self, data: pd.DataFrame, objective: str, constraints: Dict = None) -> Dict:
        """Native optimization implementation"""
        
        try:
            # Calculate returns
            returns = data.pct_change().dropna()
            
            # Calculate statistics
            mean_returns = returns.mean() * 252  # Annualized
            cov_matrix = returns.cov() * 252     # Annualized
            
            n_assets = len(data.columns)
            
            # Optimization function
            def portfolio_stats(weights):
                portfolio_return = np.sum(mean_returns * weights)
                portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
                sharpe_ratio = portfolio_return / portfolio_volatility
                return portfolio_return, portfolio_volatility, sharpe_ratio
            
            # Objective functions
            def negative_sharpe(weights):
                return -portfolio_stats(weights)[2]
            
            def portfolio_volatility(weights):
                return portfolio_stats(weights)[1]
            
            def negative_return(weights):
                return -portfolio_stats(weights)[0]
            
            # Constraints
            constraints_list = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1
            
            # Bounds
            bounds = tuple((0, 1) for _ in range(n_assets))
            
            # Add custom constraints
            if constraints:
                if 'max_weight' in constraints:
                    bounds = tuple((0, constraints['max_weight']) for _ in range(n_assets))
                if 'min_weight' in constraints:
                    bounds = tuple((constraints['min_weight'], bounds[i][1]) for i in range(n_assets))
            
            # Initial guess
            x0 = np.array([1.0 / n_assets] * n_assets)
            
            # Choose optimization function
            if objective == 'sharpe':
                opt_func = negative_sharpe
            elif objective == 'volatility':
                opt_func = portfolio_volatility
            elif objective == 'return':
                opt_func = negative_return
            else:
                opt_func = negative_sharpe
            
            # Optimize
            if SCIPY_AVAILABLE:
                result = minimize(opt_func, x0, method='SLSQP', bounds=bounds, constraints=constraints_list)
                optimal_weights = result.x
            else:
                # Simple equal weighting if scipy not available
                optimal_weights = np.array([1.0 / n_assets] * n_assets)
            
            # Calculate final statistics
            final_return, final_volatility, final_sharpe = portfolio_stats(optimal_weights)
            
            # Create weights dictionary
            weights_dict = dict(zip(data.columns, optimal_weights))
            
            # Simple allocation calculation
            total_value = constraints.get('total_value', 100000) if constraints else 100000
            allocation = {}
            for symbol, weight in weights_dict.items():
                if weight > 0.01:  # Only allocate if weight > 1%
                    allocation[symbol] = int(total_value * weight)
            
            leftover = total_value - sum(allocation.values())
            
            return {
                'method': 'native',
                'objective': objective,
                'weights': weights_dict,
                'expected_return': final_return,
                'volatility': final_volatility,
                'sharpe_ratio': final_sharpe,
                'allocation': allocation,
                'leftover_cash': leftover,
                'total_value': total_value
            }
            
        except Exception as e:
            return {'error': f'Native optimization failed: {str(e)}'}


class RIMSIRiskModels:
    """
    Advanced risk modeling and factor analysis
    """
    
    def __init__(self):
        self.risk_models = {
            'sample_covariance': True,
            'ledoit_wolf': SCIPY_AVAILABLE,
            'factor_model': SKLEARN_AVAILABLE,
            'ewma': True
        }
    
    async def calculate_risk_metrics(self, data: pd.DataFrame, model: str = 'auto') -> Dict:
        """
        Calculate comprehensive risk metrics
        """
        
        try:
            if model == 'auto':
                model = 'sample_covariance'
            
            # Calculate returns
            returns = data.pct_change().dropna()
            
            # Base risk metrics
            metrics = {
                'volatility': self._calculate_volatility(returns),
                'correlation_matrix': returns.corr().to_dict(),
                'var_metrics': self._calculate_var(returns),
                'drawdown_metrics': self._calculate_drawdown(data),
                'beta_metrics': await self._calculate_beta(data),
                'risk_contribution': self._calculate_risk_contribution(returns)
            }
            
            # Model-specific metrics
            if model == 'factor_model' and SKLEARN_AVAILABLE:
                metrics['factor_analysis'] = self._factor_analysis(returns)
            
            if model == 'ledoit_wolf' and SCIPY_AVAILABLE:
                metrics['shrinkage_covariance'] = self._ledoit_wolf_covariance(returns)
            
            metrics['model_used'] = model
            
            return metrics
            
        except Exception as e:
            return {'error': f'Risk metric calculation failed: {str(e)}'}
    
    def _calculate_volatility(self, returns: pd.DataFrame) -> Dict:
        """Calculate various volatility measures"""
        
        volatility_metrics = {}
        
        for column in returns.columns:
            asset_returns = returns[column]
            
            volatility_metrics[column] = {
                'daily_volatility': asset_returns.std(),
                'annualized_volatility': asset_returns.std() * np.sqrt(252),
                'rolling_30d_volatility': asset_returns.rolling(30).std().iloc[-1] * np.sqrt(252),
                'ewma_volatility': self._ewma_volatility(asset_returns),
                'parkinson_volatility': self._parkinson_volatility(asset_returns) if len(asset_returns) > 30 else None
            }
        
        return volatility_metrics
    
    def _ewma_volatility(self, returns: pd.Series, alpha: float = 0.94) -> float:
        """Calculate EWMA volatility"""
        
        try:
            squared_returns = returns ** 2
            ewma_var = squared_returns.ewm(alpha=alpha).mean().iloc[-1]
            return np.sqrt(ewma_var * 252)
        except:
            return returns.std() * np.sqrt(252)
    
    def _parkinson_volatility(self, returns: pd.Series) -> float:
        """Calculate Parkinson volatility (requires OHLC data - simplified here)"""
        
        # This is a placeholder - real Parkinson volatility needs OHLC data
        return returns.std() * np.sqrt(252) * 1.67  # Approximate adjustment
    
    def _calculate_var(self, returns: pd.DataFrame) -> Dict:
        """Calculate Value at Risk metrics"""
        
        var_metrics = {}
        
        for column in returns.columns:
            asset_returns = returns[column]
            
            var_metrics[column] = {
                'var_95': asset_returns.quantile(0.05),
                'var_99': asset_returns.quantile(0.01),
                'cvar_95': asset_returns[asset_returns <= asset_returns.quantile(0.05)].mean(),
                'cvar_99': asset_returns[asset_returns <= asset_returns.quantile(0.01)].mean(),
                'historical_var_95': asset_returns.quantile(0.05),
                'parametric_var_95': asset_returns.mean() - 1.645 * asset_returns.std()
            }
        
        return var_metrics
    
    def _calculate_drawdown(self, data: pd.DataFrame) -> Dict:
        """Calculate drawdown metrics"""
        
        drawdown_metrics = {}
        
        for column in data.columns:
            prices = data[column]
            
            # Calculate running maximum
            running_max = prices.expanding().max()
            
            # Calculate drawdown
            drawdown = (prices - running_max) / running_max
            
            drawdown_metrics[column] = {
                'max_drawdown': drawdown.min(),
                'current_drawdown': drawdown.iloc[-1],
                'avg_drawdown': drawdown[drawdown < 0].mean(),
                'drawdown_duration': self._calculate_drawdown_duration(drawdown),
                'recovery_time': self._calculate_recovery_time(drawdown)
            }
        
        return drawdown_metrics
    
    def _calculate_drawdown_duration(self, drawdown: pd.Series) -> int:
        """Calculate average drawdown duration"""
        
        try:
            # Find drawdown periods
            in_drawdown = drawdown < 0
            drawdown_periods = []
            
            start = None
            for i, is_dd in enumerate(in_drawdown):
                if is_dd and start is None:
                    start = i
                elif not is_dd and start is not None:
                    drawdown_periods.append(i - start)
                    start = None
            
            return int(np.mean(drawdown_periods)) if drawdown_periods else 0
            
        except:
            return 0
    
    def _calculate_recovery_time(self, drawdown: pd.Series) -> int:
        """Calculate average recovery time"""
        
        try:
            # This is a simplified calculation
            recovery_times = []
            
            in_drawdown = False
            start_idx = 0
            
            for i, dd in enumerate(drawdown):
                if dd < 0 and not in_drawdown:
                    in_drawdown = True
                    start_idx = i
                elif dd >= 0 and in_drawdown:
                    recovery_times.append(i - start_idx)
                    in_drawdown = False
            
            return int(np.mean(recovery_times)) if recovery_times else 0
            
        except:
            return 0
    
    async def _calculate_beta(self, data: pd.DataFrame, benchmark: str = 'SPY') -> Dict:
        """Calculate beta against benchmark"""
        
        beta_metrics = {}
        
        try:
            # Get benchmark data
            benchmark_data = yf.download(benchmark, period='2y', progress=False)['Close']
            benchmark_returns = benchmark_data.pct_change().dropna()
            
            # Align dates
            common_dates = data.index.intersection(benchmark_returns.index)
            
            if len(common_dates) < 50:  # Not enough data
                return {'error': 'Insufficient overlapping data for beta calculation'}
            
            benchmark_aligned = benchmark_returns.loc[common_dates]
            
            for column in data.columns:
                asset_data = data[column].loc[common_dates]
                asset_returns = asset_data.pct_change().dropna()
                
                # Align returns
                common_return_dates = asset_returns.index.intersection(benchmark_aligned.index)
                asset_aligned = asset_returns.loc[common_return_dates]
                benchmark_final = benchmark_aligned.loc[common_return_dates]
                
                if len(asset_aligned) > 30:
                    # Calculate beta
                    covariance = np.cov(asset_aligned, benchmark_final)[0, 1]
                    benchmark_variance = np.var(benchmark_final)
                    beta = covariance / benchmark_variance if benchmark_variance > 0 else 0
                    
                    # Calculate alpha
                    asset_mean = asset_aligned.mean() * 252
                    benchmark_mean = benchmark_final.mean() * 252
                    alpha = asset_mean - beta * benchmark_mean
                    
                    # Calculate correlation
                    correlation = np.corrcoef(asset_aligned, benchmark_final)[0, 1]
                    
                    beta_metrics[column] = {
                        'beta': beta,
                        'alpha': alpha,
                        'correlation': correlation,
                        'r_squared': correlation ** 2,
                        'tracking_error': (asset_aligned - benchmark_final).std() * np.sqrt(252)
                    }
                else:
                    beta_metrics[column] = {'error': 'Insufficient data'}
            
            return beta_metrics
            
        except Exception as e:
            return {'error': f'Beta calculation failed: {str(e)}'}
    
    def _calculate_risk_contribution(self, returns: pd.DataFrame) -> Dict:
        """Calculate risk contribution of each asset"""
        
        try:
            # Calculate covariance matrix
            cov_matrix = returns.cov() * 252  # Annualized
            
            # Equal weights for risk contribution calculation
            n_assets = len(returns.columns)
            weights = np.array([1.0 / n_assets] * n_assets)
            
            # Portfolio variance
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            
            # Marginal risk contributions
            marginal_contrib = np.dot(cov_matrix, weights)
            
            # Risk contributions
            risk_contrib = weights * marginal_contrib / portfolio_variance
            
            # Component risk contributions
            risk_contribution = {}
            for i, column in enumerate(returns.columns):
                risk_contribution[column] = {
                    'risk_contribution': risk_contrib[i],
                    'marginal_contribution': marginal_contrib[i],
                    'percentage_contribution': risk_contrib[i] / np.sum(risk_contrib) * 100
                }
            
            return risk_contribution
            
        except Exception as e:
            return {'error': f'Risk contribution calculation failed: {str(e)}'}
    
    def _factor_analysis(self, returns: pd.DataFrame) -> Dict:
        """Perform factor analysis using PCA"""
        
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not available for factor analysis'}
        
        try:
            # Standardize returns
            scaler = StandardScaler()
            scaled_returns = scaler.fit_transform(returns)
            
            # Perform PCA
            pca = PCA()
            pca.fit(scaled_returns)
            
            # Extract factors
            n_factors = min(5, len(returns.columns))  # Up to 5 factors
            
            factor_analysis = {
                'explained_variance_ratio': pca.explained_variance_ratio_[:n_factors].tolist(),
                'cumulative_variance': np.cumsum(pca.explained_variance_ratio_[:n_factors]).tolist(),
                'factor_loadings': {},
                'n_factors': n_factors
            }
            
            # Factor loadings
            for i, column in enumerate(returns.columns):
                factor_analysis['factor_loadings'][column] = pca.components_[:n_factors, i].tolist()
            
            return factor_analysis
            
        except Exception as e:
            return {'error': f'Factor analysis failed: {str(e)}'}
    
    def _ledoit_wolf_covariance(self, returns: pd.DataFrame) -> Dict:
        """Calculate Ledoit-Wolf shrinkage covariance matrix"""
        
        if not SCIPY_AVAILABLE:
            return {'error': 'Scipy not available for Ledoit-Wolf covariance'}
        
        try:
            from sklearn.covariance import LedoitWolf
            
            # Calculate shrinkage covariance
            lw = LedoitWolf()
            lw.fit(returns)
            
            shrinkage_cov = lw.covariance_ * 252  # Annualized
            
            return {
                'shrinkage_intensity': lw.shrinkage_,
                'covariance_matrix': pd.DataFrame(shrinkage_cov, 
                                                index=returns.columns, 
                                                columns=returns.columns).to_dict()
            }
            
        except Exception as e:
            return {'error': f'Ledoit-Wolf covariance failed: {str(e)}'}


class RIMSIPerformanceAnalyzer:
    """
    Comprehensive performance analysis and attribution
    """
    
    def __init__(self):
        pass
    
    async def analyze_performance(self, returns: pd.Series, benchmark_returns: pd.Series = None) -> Dict:
        """
        Comprehensive performance analysis
        """
        
        try:
            analysis = {
                'return_metrics': self._calculate_return_metrics(returns),
                'risk_metrics': self._calculate_risk_metrics_series(returns),
                'efficiency_metrics': self._calculate_efficiency_metrics(returns)
            }
            
            # Benchmark comparison if provided
            if benchmark_returns is not None:
                analysis['benchmark_comparison'] = self._compare_to_benchmark(returns, benchmark_returns)
            
            # Risk-adjusted metrics
            analysis['risk_adjusted_metrics'] = self._calculate_risk_adjusted_metrics(returns)
            
            # Tail risk metrics
            analysis['tail_risk_metrics'] = self._calculate_tail_risk_metrics(returns)
            
            return analysis
            
        except Exception as e:
            return {'error': f'Performance analysis failed: {str(e)}'}
    
    def _calculate_return_metrics(self, returns: pd.Series) -> Dict:
        """Calculate return-based metrics"""
        
        return {
            'total_return': (1 + returns).prod() - 1,
            'annualized_return': (1 + returns.mean()) ** 252 - 1,
            'geometric_mean': ((1 + returns).prod()) ** (1 / len(returns)) - 1,
            'arithmetic_mean': returns.mean(),
            'median_return': returns.median(),
            'best_day': returns.max(),
            'worst_day': returns.min(),
            'positive_days': (returns > 0).sum(),
            'negative_days': (returns < 0).sum(),
            'win_rate': (returns > 0).mean()
        }
    
    def _calculate_risk_metrics_series(self, returns: pd.Series) -> Dict:
        """Calculate risk metrics for a return series"""
        
        return {
            'volatility': returns.std() * np.sqrt(252),
            'downside_deviation': returns[returns < 0].std() * np.sqrt(252),
            'semi_deviation': returns[returns < returns.mean()].std() * np.sqrt(252),
            'var_95': returns.quantile(0.05),
            'var_99': returns.quantile(0.01),
            'cvar_95': returns[returns <= returns.quantile(0.05)].mean(),
            'cvar_99': returns[returns <= returns.quantile(0.01)].mean(),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'jarque_bera': self._jarque_bera_test(returns)
        }
    
    def _calculate_efficiency_metrics(self, returns: pd.Series) -> Dict:
        """Calculate efficiency and risk-adjusted metrics"""
        
        annualized_return = (1 + returns.mean()) ** 252 - 1
        volatility = returns.std() * np.sqrt(252)
        downside_deviation = returns[returns < 0].std() * np.sqrt(252)
        
        return {
            'sharpe_ratio': annualized_return / volatility if volatility > 0 else 0,
            'sortino_ratio': annualized_return / downside_deviation if downside_deviation > 0 else 0,
            'calmar_ratio': annualized_return / abs(self._max_drawdown(returns)) if self._max_drawdown(returns) != 0 else 0,
            'sterling_ratio': annualized_return / abs(self._average_drawdown(returns)) if self._average_drawdown(returns) != 0 else 0,
            'burke_ratio': annualized_return / np.sqrt(np.sum(self._drawdown_periods(returns) ** 2)) if len(self._drawdown_periods(returns)) > 0 else 0
        }
    
    def _calculate_risk_adjusted_metrics(self, returns: pd.Series) -> Dict:
        """Calculate additional risk-adjusted metrics"""
        
        excess_returns = returns - 0.02/252  # Assuming 2% risk-free rate
        
        return {
            'information_ratio': excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0,
            'modigliani_ratio': self._modigliani_ratio(returns),
            'treynor_ratio': self._treynor_ratio(returns),
            'jensen_alpha': self._jensen_alpha(returns)
        }
    
    def _calculate_tail_risk_metrics(self, returns: pd.Series) -> Dict:
        """Calculate tail risk metrics"""
        
        return {
            'tail_ratio': returns.quantile(0.95) / abs(returns.quantile(0.05)),
            'gain_pain_ratio': returns[returns > 0].sum() / abs(returns[returns < 0].sum()) if returns[returns < 0].sum() != 0 else 0,
            'upside_capture': returns[returns > 0].mean() / returns.mean() if returns.mean() > 0 else 0,
            'downside_capture': abs(returns[returns < 0].mean()) / abs(returns.mean()) if returns.mean() < 0 else 0,
            'omega_ratio': self._omega_ratio(returns)
        }
    
    def _compare_to_benchmark(self, returns: pd.Series, benchmark_returns: pd.Series) -> Dict:
        """Compare performance to benchmark"""
        
        try:
            # Align returns
            common_dates = returns.index.intersection(benchmark_returns.index)
            returns_aligned = returns.loc[common_dates]
            benchmark_aligned = benchmark_returns.loc[common_dates]
            
            excess_returns = returns_aligned - benchmark_aligned
            
            return {
                'alpha': excess_returns.mean() * 252,
                'beta': np.cov(returns_aligned, benchmark_aligned)[0, 1] / np.var(benchmark_aligned),
                'correlation': np.corrcoef(returns_aligned, benchmark_aligned)[0, 1],
                'tracking_error': excess_returns.std() * np.sqrt(252),
                'information_ratio': excess_returns.mean() / excess_returns.std() if excess_returns.std() > 0 else 0,
                'upside_capture': self._upside_capture(returns_aligned, benchmark_aligned),
                'downside_capture': self._downside_capture(returns_aligned, benchmark_aligned)
            }
            
        except Exception as e:
            return {'error': f'Benchmark comparison failed: {str(e)}'}
    
    # Helper methods
    def _max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def _average_drawdown(self, returns: pd.Series) -> float:
        """Calculate average drawdown"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown[drawdown < 0].mean()
    
    def _drawdown_periods(self, returns: pd.Series) -> np.ndarray:
        """Get drawdown periods"""
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown[drawdown < 0].values
    
    def _jarque_bera_test(self, returns: pd.Series) -> Dict:
        """Jarque-Bera normality test"""
        try:
            from scipy.stats import jarque_bera
            statistic, p_value = jarque_bera(returns.dropna())
            return {'statistic': statistic, 'p_value': p_value, 'is_normal': p_value > 0.05}
        except:
            return {'error': 'Jarque-Bera test failed'}
    
    def _modigliani_ratio(self, returns: pd.Series) -> float:
        """Calculate Modigliani risk-adjusted performance"""
        try:
            annualized_return = (1 + returns.mean()) ** 252 - 1
            volatility = returns.std() * np.sqrt(252)
            market_volatility = 0.16  # Assumed market volatility
            return annualized_return * (market_volatility / volatility) if volatility > 0 else 0
        except:
            return 0
    
    def _treynor_ratio(self, returns: pd.Series) -> float:
        """Calculate Treynor ratio (simplified without beta)"""
        try:
            annualized_return = (1 + returns.mean()) ** 252 - 1
            # Simplified - would need market data for proper beta calculation
            beta = 1.0  # Assumed beta
            return annualized_return / beta
        except:
            return 0
    
    def _jensen_alpha(self, returns: pd.Series) -> float:
        """Calculate Jensen's alpha (simplified)"""
        try:
            annualized_return = (1 + returns.mean()) ** 252 - 1
            risk_free_rate = 0.02
            market_return = 0.08  # Assumed market return
            beta = 1.0  # Assumed beta
            return annualized_return - (risk_free_rate + beta * (market_return - risk_free_rate))
        except:
            return 0
    
    def _omega_ratio(self, returns: pd.Series, threshold: float = 0) -> float:
        """Calculate Omega ratio"""
        try:
            gains = returns[returns > threshold].sum()
            losses = abs(returns[returns <= threshold].sum())
            return gains / losses if losses > 0 else 0
        except:
            return 0
    
    def _upside_capture(self, returns: pd.Series, benchmark: pd.Series) -> float:
        """Calculate upside capture ratio"""
        try:
            up_periods = benchmark > 0
            portfolio_up = returns[up_periods].mean()
            benchmark_up = benchmark[up_periods].mean()
            return portfolio_up / benchmark_up if benchmark_up > 0 else 0
        except:
            return 0
    
    def _downside_capture(self, returns: pd.Series, benchmark: pd.Series) -> float:
        """Calculate downside capture ratio"""
        try:
            down_periods = benchmark < 0
            portfolio_down = returns[down_periods].mean()
            benchmark_down = benchmark[down_periods].mean()
            return portfolio_down / benchmark_down if benchmark_down < 0 else 0
        except:
            return 0


# Global instances
_rimsi_portfolio_optimizer = None
_rimsi_risk_models = None
_rimsi_performance_analyzer = None

def get_rimsi_portfolio_optimizer():
    """Get global portfolio optimizer instance"""
    global _rimsi_portfolio_optimizer
    if _rimsi_portfolio_optimizer is None:
        _rimsi_portfolio_optimizer = RIMSIPortfolioOptimizer()
    return _rimsi_portfolio_optimizer

def get_rimsi_risk_models():
    """Get global risk models instance"""
    global _rimsi_risk_models
    if _rimsi_risk_models is None:
        _rimsi_risk_models = RIMSIRiskModels()
    return _rimsi_risk_models

def get_rimsi_performance_analyzer():
    """Get global performance analyzer instance"""
    global _rimsi_performance_analyzer
    if _rimsi_performance_analyzer is None:
        _rimsi_performance_analyzer = RIMSIPerformanceAnalyzer()
    return _rimsi_performance_analyzer
