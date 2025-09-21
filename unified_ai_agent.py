"""
Unified AI Agent for Portfolio Analysis
=====================================

Anthropic Sonnet 3.5 powered AI agent that combines multiple ML models
to provide real-time portfolio insights and actionable recommendations.

Author: RIMSI AI System  
Date: September 2025
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
import asyncio
import os

# Import specialized models
try:
    from specialized_ml_models import AdvancedVolatilityModel, AdvancedSharpeRatioModel, get_specialized_ml_models
    SPECIALIZED_MODELS_AVAILABLE = True
except ImportError:
    SPECIALIZED_MODELS_AVAILABLE = False

# Import existing RIMSI models
try:
    from rimsi_ml_models import RIMSIMLModels
    RIMSI_MODELS_AVAILABLE = True
except ImportError:
    RIMSI_MODELS_AVAILABLE = False

# Import Anthropic client
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import data providers
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

logger = logging.getLogger(__name__)

class UnifiedPortfolioAgent:
    """
    Unified AI Agent powered by Anthropic Sonnet 3.5
    
    Features:
    - Multi-model ML integration
    - Real-time market data analysis
    - Portfolio-specific insights
    - Actionable recommendations with confidence scores
    """
    
    def __init__(self, selected_models: List[str], anthropic_api_key: str = None):
        self.agent_id = f"unified_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.selected_models = selected_models
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.anthropic_client = None
        self.ml_models = {}
        self.analysis_cache = {}
        self.confidence_threshold = 0.70
        
        # Initialize Anthropic client
        if ANTHROPIC_AVAILABLE and self.anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
                logger.info("✅ Anthropic Sonnet 3.5 client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Anthropic client: {e}")
        
        # Initialize selected ML models
        self._initialize_ml_models()
        
        # Agent personality and role
        self.agent_role = "Balanced Portfolio Analyst"
        self.analysis_style = "data-driven with conservative risk assessment"
        
    def _initialize_ml_models(self):
        """Initialize the selected ML models"""
        try:
            # Initialize specialized models
            if SPECIALIZED_MODELS_AVAILABLE:
                for model_id in self.selected_models:
                    if 'volatility' in model_id.lower():
                        self.ml_models['volatility'] = AdvancedVolatilityModel()
                        logger.info("✅ Advanced Volatility Model initialized")
                    elif 'sharpe' in model_id.lower():
                        self.ml_models['sharpe'] = AdvancedSharpeRatioModel()
                        logger.info("✅ Advanced Sharpe Ratio Model initialized")
            
            # Initialize RIMSI models if available
            if RIMSI_MODELS_AVAILABLE and len(self.ml_models) < len(self.selected_models):
                rimsi_registry = RIMSIMLModels()
                for model_id in self.selected_models:
                    if model_id in rimsi_registry.models:
                        self.ml_models[model_id] = rimsi_registry.models[model_id]
                        logger.info(f"✅ RIMSI Model {model_id} initialized")
                        
        except Exception as e:
            logger.error(f"❌ Error initializing ML models: {e}")
    
    def fetch_market_data(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """Fetch real-time market data using yfinance"""
        market_data = {}
        
        if not YFINANCE_AVAILABLE:
            logger.warning("⚠️ yfinance not available, using mock data")
            return self._generate_mock_data(symbols)
        
        try:
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period)
                
                if not data.empty:
                    # Add additional metrics
                    data['returns'] = data['Close'].pct_change()
                    data['volatility'] = data['returns'].rolling(20).std() * np.sqrt(252)
                    data['volume_ma'] = data['Volume'].rolling(20).mean()
                    
                    market_data[symbol] = data.copy()
                    logger.info(f"✅ Fetched data for {symbol}: {len(data)} periods")
                else:
                    logger.warning(f"⚠️ No data available for {symbol}")
                    
        except Exception as e:
            logger.error(f"❌ Error fetching market data: {e}")
            return self._generate_mock_data(symbols)
        
        return market_data
    
    def _generate_mock_data(self, symbols: List[str]) -> Dict[str, pd.DataFrame]:
        """Generate mock market data for testing"""
        mock_data = {}
        dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
        
        for symbol in symbols:
            np.random.seed(hash(symbol) % (2**32))  # Consistent mock data per symbol
            
            # Generate realistic price data
            returns = np.random.normal(0.001, 0.02, len(dates))  # Daily returns
            prices = [100]  # Starting price
            
            for ret in returns[1:]:
                prices.append(prices[-1] * (1 + ret))
            
            # Create DataFrame
            data = pd.DataFrame({
                'Open': prices,
                'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
                'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
                'Close': prices,
                'Volume': np.random.randint(1000000, 10000000, len(dates))
            }, index=dates)
            
            # Add calculated fields
            data['returns'] = data['Close'].pct_change()
            data['volatility'] = data['returns'].rolling(20).std() * np.sqrt(252)
            data['volume_ma'] = data['Volume'].rolling(20).mean()
            
            mock_data[symbol] = data
            
        return mock_data
    
    def analyze_portfolio(self, portfolio_data: Dict[str, Any], 
                         market_data: Dict[str, pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Comprehensive portfolio analysis using selected ML models
        """
        try:
            analysis_results = {
                'agent_id': self.agent_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'portfolio_summary': portfolio_data,
                'ml_analyses': {},
                'overall_confidence': 0.0,
                'recommendations': [],
                'risk_assessment': {},
                'performance_metrics': {}
            }
            
            # Fetch market data if not provided
            if market_data is None:
                symbols = [stock['ticker'] for stock in portfolio_data.get('holdings', [])]
                market_data = self.fetch_market_data(symbols)
            
            # Run ML model analyses
            confidence_scores = []
            
            # Volatility Analysis
            if 'volatility' in self.ml_models:
                vol_results = self._run_volatility_analysis(portfolio_data, market_data)
                analysis_results['ml_analyses']['volatility'] = vol_results
                confidence_scores.append(vol_results.get('confidence_score', 0.5))
            
            # Sharpe Ratio Analysis  
            if 'sharpe' in self.ml_models:
                sharpe_results = self._run_sharpe_analysis(portfolio_data, market_data)
                analysis_results['ml_analyses']['sharpe'] = sharpe_results
                confidence_scores.append(sharpe_results.get('confidence_score', 0.5))
            
            # Calculate overall confidence
            analysis_results['overall_confidence'] = np.mean(confidence_scores) if confidence_scores else 0.5
            
            # Generate risk assessment
            analysis_results['risk_assessment'] = self._assess_portfolio_risk(analysis_results['ml_analyses'])
            
            # Generate performance metrics
            analysis_results['performance_metrics'] = self._calculate_performance_metrics(portfolio_data, market_data)
            
            # Cache results
            self.analysis_cache[portfolio_data.get('portfolio_id', 'default')] = analysis_results
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"❌ Portfolio analysis error: {e}")
            return {
                'agent_id': self.agent_id,
                'status': 'error',
                'error_message': str(e),
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _run_volatility_analysis(self, portfolio_data: Dict[str, Any], 
                               market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Run volatility analysis on portfolio"""
        volatility_model = self.ml_models['volatility']
        vol_results = {}
        
        try:
            for holding in portfolio_data.get('holdings', []):
                symbol = holding['ticker']
                if symbol in market_data:
                    symbol_data = market_data[symbol]
                    
                    # Convert column names to lowercase for consistency
                    symbol_data.columns = [col.lower() for col in symbol_data.columns]
                    
                    vol_prediction = volatility_model.predict_volatility(symbol_data)
                    vol_results[symbol] = vol_prediction
            
            # Portfolio-level volatility
            portfolio_vol = self._calculate_portfolio_volatility(portfolio_data, vol_results)
            vol_results['portfolio_volatility'] = portfolio_vol
            
            return vol_results
            
        except Exception as e:
            logger.error(f"❌ Volatility analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _run_sharpe_analysis(self, portfolio_data: Dict[str, Any], 
                           market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Run Sharpe ratio analysis on portfolio"""
        sharpe_model = self.ml_models['sharpe']
        sharpe_results = {}
        
        try:
            for holding in portfolio_data.get('holdings', []):
                symbol = holding['ticker']
                if symbol in market_data:
                    symbol_data = market_data[symbol]
                    
                    # Convert column names to lowercase for consistency
                    symbol_data.columns = [col.lower() for col in symbol_data.columns]
                    
                    sharpe_prediction = sharpe_model.predict_sharpe_ratio(symbol_data)
                    sharpe_results[symbol] = sharpe_prediction
            
            # Portfolio-level Sharpe ratio
            portfolio_sharpe = self._calculate_portfolio_sharpe(portfolio_data, market_data)
            sharpe_results['portfolio_sharpe'] = portfolio_sharpe
            
            return sharpe_results
            
        except Exception as e:
            logger.error(f"❌ Sharpe analysis error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_portfolio_volatility(self, portfolio_data: Dict[str, Any], 
                                      vol_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate portfolio-level volatility metrics"""
        try:
            holdings = portfolio_data.get('holdings', [])
            total_value = sum(h.get('market_value', h.get('quantity', 0) * h.get('current_price', 0)) for h in holdings)
            
            if total_value == 0:
                return {'status': 'error', 'message': 'no portfolio value'}
            
            weighted_vol = 0
            risk_contribution = {}
            
            for holding in holdings:
                symbol = holding['ticker']
                weight = (holding.get('market_value', holding.get('quantity', 0) * holding.get('current_price', 0))) / total_value
                
                if symbol in vol_results and 'predicted_volatility' in vol_results[symbol]:
                    vol = vol_results[symbol]['predicted_volatility']
                    weighted_vol += weight * vol
                    risk_contribution[symbol] = weight * vol
            
            return {
                'portfolio_volatility': weighted_vol,
                'risk_contribution': risk_contribution,
                'diversification_ratio': len(holdings) / max(1, weighted_vol * 10),  # Simple diversification metric
                'status': 'success'
            }
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _calculate_portfolio_sharpe(self, portfolio_data: Dict[str, Any], 
                                  market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate portfolio-level Sharpe ratio"""
        try:
            holdings = portfolio_data.get('holdings', [])
            
            # Calculate portfolio returns
            portfolio_returns = []
            weights = {}
            total_value = sum(h.get('market_value', h.get('quantity', 0) * h.get('current_price', 0)) for h in holdings)
            
            if total_value == 0:
                return {'status': 'error', 'message': 'no portfolio value'}
            
            for holding in holdings:
                symbol = holding['ticker']
                weight = (holding.get('market_value', holding.get('quantity', 0) * holding.get('current_price', 0))) / total_value
                weights[symbol] = weight
            
            # Get minimum common date range
            if market_data:
                common_dates = None
                for symbol in weights.keys():
                    if symbol in market_data:
                        if common_dates is None:
                            common_dates = market_data[symbol].index
                        else:
                            common_dates = common_dates.intersection(market_data[symbol].index)
                
                if common_dates is not None and len(common_dates) > 0:
                    # Calculate weighted portfolio returns
                    portfolio_returns = pd.Series(0, index=common_dates)
                    
                    for symbol, weight in weights.items():
                        if symbol in market_data:
                            symbol_returns = market_data[symbol]['returns'].reindex(common_dates).fillna(0)
                            portfolio_returns += weight * symbol_returns
                    
                    # Calculate Sharpe ratio
                    annual_return = portfolio_returns.mean() * 252
                    annual_volatility = portfolio_returns.std() * np.sqrt(252)
                    risk_free_rate = 0.05  # 5% annual
                    
                    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
                    
                    return {
                        'portfolio_sharpe': sharpe_ratio,
                        'annual_return': annual_return,
                        'annual_volatility': annual_volatility,
                        'risk_free_rate': risk_free_rate,
                        'status': 'success'
                    }
            
            return {'status': 'error', 'message': 'insufficient data'}
            
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _assess_portfolio_risk(self, ml_analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall portfolio risk based on ML analyses"""
        risk_factors = []
        risk_level = "MODERATE"
        
        # Volatility risk assessment
        if 'volatility' in ml_analyses:
            vol_data = ml_analyses['volatility']
            if 'portfolio_volatility' in vol_data:
                portfolio_vol = vol_data['portfolio_volatility'].get('portfolio_volatility', 0.2)
                if portfolio_vol > 0.3:
                    risk_factors.append("HIGH_VOLATILITY")
                elif portfolio_vol > 0.2:
                    risk_factors.append("ELEVATED_VOLATILITY")
        
        # Sharpe ratio risk assessment
        if 'sharpe' in ml_analyses:
            sharpe_data = ml_analyses['sharpe']
            if 'portfolio_sharpe' in sharpe_data:
                portfolio_sharpe = sharpe_data['portfolio_sharpe'].get('portfolio_sharpe', 1.0)
                if portfolio_sharpe < 0.5:
                    risk_factors.append("LOW_RISK_ADJUSTED_RETURN")
                elif portfolio_sharpe < 1.0:
                    risk_factors.append("MODERATE_RISK_ADJUSTED_RETURN")
        
        # Determine overall risk level
        if len(risk_factors) >= 2 or "HIGH_VOLATILITY" in risk_factors:
            risk_level = "HIGH"
        elif len(risk_factors) == 1:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'risk_score': len(risk_factors) / 4.0,  # Normalized risk score
            'assessment_timestamp': datetime.now().isoformat()
        }
    
    def _calculate_performance_metrics(self, portfolio_data: Dict[str, Any], 
                                     market_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            holdings = portfolio_data.get('holdings', [])
            
            metrics = {
                'total_positions': len(holdings),
                'total_market_value': 0,
                'top_holdings': [],
                'sector_allocation': {},
                'performance_summary': {}
            }
            
            # Calculate basic metrics
            for holding in holdings:
                market_value = holding.get('market_value', holding.get('quantity', 0) * holding.get('current_price', 0))
                metrics['total_market_value'] += market_value
                
                # Top holdings (by value)
                metrics['top_holdings'].append({
                    'symbol': holding['ticker'],
                    'market_value': market_value,
                    'weight': 0  # Will calculate after total
                })
            
            # Calculate weights and sort top holdings
            if metrics['total_market_value'] > 0:
                for holding in metrics['top_holdings']:
                    holding['weight'] = holding['market_value'] / metrics['total_market_value']
                
                metrics['top_holdings'] = sorted(metrics['top_holdings'], 
                                               key=lambda x: x['market_value'], reverse=True)[:5]
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Performance metrics calculation error: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def generate_anthropic_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI insights using Anthropic Sonnet 3.5"""
        if not self.anthropic_client:
            return self._generate_fallback_insights(analysis_results)
        
        try:
            # Prepare context for Anthropic
            context = self._prepare_anthropic_context(analysis_results)
            
            # Create prompt for Anthropic Sonnet 3.5
            prompt = f"""
            You are an expert portfolio analyst AI agent with access to advanced ML models. 
            
            Role: {self.agent_role}
            Analysis Style: {self.analysis_style}
            
            Portfolio Analysis Context:
            {json.dumps(context, indent=2)}
            
            Based on this comprehensive analysis from multiple ML models, provide:
            
            1. Executive Summary (2-3 sentences)
            2. Key Insights (3-5 bullet points)
            3. Actionable Recommendations (3-5 specific actions with confidence scores 0-100)
            4. Risk Assessment Summary
            5. Market Outlook (short-term and medium-term)
            
            Format your response as JSON with the following structure:
            {{
                "executive_summary": "...",
                "key_insights": ["...", "...", "..."],
                "recommendations": [
                    {{"action": "...", "reasoning": "...", "confidence": 85, "priority": "HIGH"}},
                    ...
                ],
                "risk_assessment": "...",
                "market_outlook": {{"short_term": "...", "medium_term": "..."}}
            }}
            
            Be specific, data-driven, and provide actionable insights that an investor can act upon immediately.
            """
            
            response = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse Anthropic response
            ai_insights = json.loads(response.content[0].text)
            
            # Add metadata
            ai_insights['ai_model'] = 'claude-3-5-sonnet-20241022'
            ai_insights['generation_timestamp'] = datetime.now().isoformat()
            ai_insights['agent_confidence'] = analysis_results.get('overall_confidence', 0.7)
            
            return ai_insights
            
        except Exception as e:
            logger.error(f"❌ Anthropic insights generation error: {e}")
            return self._generate_fallback_insights(analysis_results)
    
    def _prepare_anthropic_context(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context data for Anthropic analysis"""
        context = {
            'portfolio_overview': {
                'total_positions': analysis_results.get('performance_metrics', {}).get('total_positions', 0),
                'total_value': analysis_results.get('performance_metrics', {}).get('total_market_value', 0),
                'analysis_confidence': analysis_results.get('overall_confidence', 0.5)
            },
            'risk_metrics': analysis_results.get('risk_assessment', {}),
            'ml_insights': {}
        }
        
        # Summarize ML analysis results
        if 'volatility' in analysis_results.get('ml_analyses', {}):
            vol_data = analysis_results['ml_analyses']['volatility']
            context['ml_insights']['volatility'] = {
                'portfolio_volatility': vol_data.get('portfolio_volatility', {}),
                'risk_level': vol_data.get('portfolio_volatility', {}).get('portfolio_volatility', 0.2)
            }
        
        if 'sharpe' in analysis_results.get('ml_analyses', {}):
            sharpe_data = analysis_results['ml_analyses']['sharpe']
            context['ml_insights']['sharpe_ratio'] = {
                'portfolio_sharpe': sharpe_data.get('portfolio_sharpe', {}),
                'risk_adjusted_performance': sharpe_data.get('portfolio_sharpe', {}).get('portfolio_sharpe', 1.0)
            }
        
        return context
    
    def _generate_fallback_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback insights when Anthropic is not available"""
        try:
            risk_level = analysis_results.get('risk_assessment', {}).get('risk_level', 'MODERATE')
            confidence = analysis_results.get('overall_confidence', 0.5)
            
            # Generate rule-based insights
            insights = {
                "executive_summary": f"Portfolio analysis completed with {confidence:.1%} confidence. Risk level assessed as {risk_level}.",
                "key_insights": [
                    f"Portfolio risk level: {risk_level}",
                    f"Analysis confidence: {confidence:.1%}",
                    "Detailed ML model analysis available"
                ],
                "recommendations": [
                    {
                        "action": "Review portfolio diversification",
                        "reasoning": "Regular diversification review recommended",
                        "confidence": 70,
                        "priority": "MEDIUM"
                    }
                ],
                "risk_assessment": f"Current portfolio risk level is {risk_level}",
                "market_outlook": {
                    "short_term": "Maintain current allocation pending further analysis",
                    "medium_term": "Consider rebalancing based on model outputs"
                },
                "ai_model": "fallback_analysis",
                "generation_timestamp": datetime.now().isoformat(),
                "agent_confidence": confidence
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Fallback insights generation error: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "generation_timestamp": datetime.now().isoformat()
            }
    
    def get_real_time_insights(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive real-time portfolio insights"""
        try:
            # Step 1: Analyze portfolio with ML models
            logger.info("🔄 Starting portfolio analysis...")
            analysis_results = self.analyze_portfolio(portfolio_data)
            
            # Step 2: Generate AI insights using Anthropic
            logger.info("🤖 Generating AI insights with Anthropic Sonnet 3.5...")
            ai_insights = self.generate_anthropic_insights(analysis_results)
            
            # Step 3: Combine results
            final_insights = {
                'agent_info': {
                    'agent_id': self.agent_id,
                    'selected_models': self.selected_models,
                    'agent_role': self.agent_role
                },
                'technical_analysis': analysis_results,
                'ai_insights': ai_insights,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            logger.info("✅ Real-time insights generation completed")
            return final_insights
            
        except Exception as e:
            logger.error(f"❌ Real-time insights error: {e}")
            return {
                'agent_id': self.agent_id,
                'status': 'error',
                'error_message': str(e),
                'timestamp': datetime.now().isoformat()
            }


def create_unified_agent(selected_models: List[str], anthropic_api_key: str = None) -> UnifiedPortfolioAgent:
    """Factory function to create unified portfolio agent"""
    return UnifiedPortfolioAgent(selected_models, anthropic_api_key)


# Example usage and testing
if __name__ == "__main__":
    # Test the unified agent
    test_models = ['advanced_volatility_v1', 'advanced_sharpe_v1']
    agent = create_unified_agent(test_models)
    
    # Test portfolio data
    test_portfolio = {
        'portfolio_id': 'test_portfolio_1',
        'holdings': [
            {'ticker': 'AAPL', 'quantity': 100, 'current_price': 150.0, 'market_value': 15000},
            {'ticker': 'GOOGL', 'quantity': 50, 'current_price': 2500.0, 'market_value': 125000},
            {'ticker': 'MSFT', 'quantity': 75, 'current_price': 300.0, 'market_value': 22500}
        ]
    }
    
    # Get insights
    insights = agent.get_real_time_insights(test_portfolio)
    print(json.dumps(insights, indent=2, default=str))