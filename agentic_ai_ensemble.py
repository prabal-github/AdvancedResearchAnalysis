#!/usr/bin/env python3
"""
RIMSI Trading Terminal - Agentic AI System
Advanced AI agents for portfolio analysis and insights generation using ML ensemble
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
import concurrent.futures
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRole(Enum):
    """AI Agent Roles in the Ensemble"""
    RISK_MANAGER = "risk_manager"
    PORTFOLIO_OPTIMIZER = "portfolio_optimizer"
    SENTIMENT_ANALYST = "sentiment_analyst"
    TECHNICAL_ANALYST = "technical_analyst"
    FUNDAMENTAL_ANALYST = "fundamental_analyst"
    MARKET_TIMER = "market_timer"
    VOLATILITY_EXPERT = "volatility_expert"
    COORDINATOR = "coordinator"

class AgentMode(Enum):
    """Agent Interaction Modes"""
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"

@dataclass
class AgentDecision:
    """Individual agent decision structure"""
    agent_id: str
    role: AgentRole
    decision: str
    confidence: float
    reasoning: str
    supporting_data: Dict[str, Any]
    timestamp: datetime
    model_predictions: Dict[str, Any]

@dataclass
class EnsembleInsight:
    """Final ensemble insight structure"""
    insight_type: str
    title: str
    description: str
    confidence: float
    severity: str  # low, medium, high
    recommendation: str
    supporting_agents: List[str]
    conflicting_agents: List[str]
    data_sources: List[str]
    timestamp: datetime

class AgenticMLAgent:
    """Individual AI Agent in the Ensemble"""
    
    def __init__(self, agent_id: str, role: AgentRole, assigned_models: List[str], 
                 rimsi_model_registry=None):
        self.agent_id = agent_id
        self.role = role
        self.assigned_models = assigned_models
        self.model_registry = rimsi_model_registry
        self.decision_history = []
        self.performance_metrics = {
            'total_decisions': 0,
            'accurate_decisions': 0,
            'confidence_score': 0.0
        }
    
    def analyze_portfolio(self, portfolio_data: Dict[str, Any], 
                         market_data: Dict[str, Any]) -> AgentDecision:
        """Generate agent-specific analysis of portfolio"""
        try:
            # Run assigned ML models
            model_predictions = self._run_assigned_models(portfolio_data, market_data)
            
            # Generate role-specific insights
            decision_data = self._generate_role_specific_analysis(
                portfolio_data, market_data, model_predictions
            )
            
            # Create decision
            decision = AgentDecision(
                agent_id=self.agent_id,
                role=self.role,
                decision=decision_data['decision'],
                confidence=decision_data['confidence'],
                reasoning=decision_data['reasoning'],
                supporting_data=decision_data['supporting_data'],
                timestamp=datetime.now(),
                model_predictions=model_predictions
            )
            
            self.decision_history.append(decision)
            self.performance_metrics['total_decisions'] += 1
            
            return decision
            
        except Exception as e:
            logger.error(f"Agent {self.agent_id} analysis error: {e}")
            return self._create_error_decision(str(e))
    
    def _run_assigned_models(self, portfolio_data: Dict[str, Any], 
                           market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run ML models assigned to this agent"""
        predictions = {}
        
        if not self.model_registry:
            return predictions
        
        for model_name in self.assigned_models:
            try:
                # Prepare data based on model type
                model_data = self._prepare_model_data(model_name, portfolio_data, market_data)
                
                # Make prediction
                result = self.model_registry.predict(model_name, model_data)
                
                if result.get('success'):
                    predictions[model_name] = result['prediction']
                else:
                    logger.warning(f"Model {model_name} prediction failed: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error running model {model_name}: {e}")
        
        return predictions
    
    def _prepare_model_data(self, model_name: str, portfolio_data: Dict[str, Any], 
                          market_data: Dict[str, Any]) -> Any:
        """Prepare data specific to model requirements"""
        # Extract symbols from portfolio
        symbols = portfolio_data.get('symbols', [])
        
        if not symbols:
            return []
        
        # Generate sample data based on model type
        if 'volatility' in model_name.lower():
            # Volatility models need return series
            return [np.random.normal(0.001, 0.02) for _ in range(50)]
        
        elif 'price' in model_name.lower():
            # Price models need price series
            base_price = 100
            returns = [np.random.normal(0.001, 0.02) for _ in range(50)]
            prices = [base_price]
            for ret in returns:
                prices.append(prices[-1] * (1 + ret))
            return prices
        
        elif 'portfolio' in model_name.lower():
            # Portfolio models need multi-asset data
            mock_data = {}
            for symbol in symbols[:5]:  # Limit to 5 symbols for performance
                returns = [np.random.normal(0.001, 0.02) for _ in range(50)]
                mock_data[symbol] = returns
            return mock_data
        
        else:
            # Default: return series
            return [np.random.normal(0.001, 0.02) for _ in range(50)]
    
    def _generate_role_specific_analysis(self, portfolio_data: Dict[str, Any], 
                                       market_data: Dict[str, Any], 
                                       model_predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis specific to agent role"""
        
        if self.role == AgentRole.RISK_MANAGER:
            return self._risk_manager_analysis(portfolio_data, model_predictions)
        
        elif self.role == AgentRole.PORTFOLIO_OPTIMIZER:
            return self._portfolio_optimizer_analysis(portfolio_data, model_predictions)
        
        elif self.role == AgentRole.SENTIMENT_ANALYST:
            return self._sentiment_analyst_analysis(portfolio_data, model_predictions)
        
        elif self.role == AgentRole.TECHNICAL_ANALYST:
            return self._technical_analyst_analysis(portfolio_data, model_predictions)
        
        elif self.role == AgentRole.VOLATILITY_EXPERT:
            return self._volatility_expert_analysis(portfolio_data, model_predictions)
        
        else:
            return self._generic_analysis(portfolio_data, model_predictions)
    
    def _risk_manager_analysis(self, portfolio_data: Dict[str, Any], 
                             predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Risk manager specific analysis"""
        risk_scores = []
        risk_factors = []
        
        for model_name, prediction in predictions.items():
            if 'risk' in model_name.lower() or 'tail' in model_name.lower():
                if isinstance(prediction, dict):
                    var_data = prediction.get('var', {})
                    if var_data:
                        var_95 = var_data.get('95.0%', {}).get('return', 0)
                        if var_95 < -0.03:
                            risk_scores.append(0.8)
                            risk_factors.append(f"High VaR risk detected: {var_95:.2%}")
                        elif var_95 < -0.02:
                            risk_scores.append(0.6)
                            risk_factors.append(f"Moderate VaR risk: {var_95:.2%}")
                        else:
                            risk_scores.append(0.3)
        
        avg_risk_score = np.mean(risk_scores) if risk_scores else 0.5
        
        if avg_risk_score > 0.7:
            decision = "HIGH_RISK_ALERT"
            confidence = 0.85
            reasoning = f"Portfolio showing high risk signals. {'; '.join(risk_factors)}"
        elif avg_risk_score > 0.5:
            decision = "MODERATE_RISK"
            confidence = 0.70
            reasoning = f"Moderate risk levels detected. {'; '.join(risk_factors)}"
        else:
            decision = "LOW_RISK"
            confidence = 0.75
            reasoning = "Portfolio risk levels appear acceptable"
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'supporting_data': {
                'risk_scores': risk_scores,
                'risk_factors': risk_factors,
                'avg_risk_score': avg_risk_score
            }
        }
    
    def _portfolio_optimizer_analysis(self, portfolio_data: Dict[str, Any], 
                                    predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Portfolio optimizer specific analysis"""
        optimization_signals = []
        rebalancing_needed = False
        
        for model_name, prediction in predictions.items():
            if 'portfolio' in model_name.lower() or 'optimization' in model_name.lower():
                if isinstance(prediction, dict):
                    allocation = prediction.get('allocation', {})
                    sharpe_ratio = prediction.get('sharpe_ratio', 0)
                    
                    if sharpe_ratio > 1.5:
                        optimization_signals.append("Excellent risk-adjusted returns")
                    elif sharpe_ratio < 0.8:
                        optimization_signals.append("Poor risk-adjusted returns - rebalancing recommended")
                        rebalancing_needed = True
                    
                    # Check for concentration risk
                    if allocation:
                        max_weight = max(allocation.values())
                        if max_weight > 0.4:
                            optimization_signals.append(f"High concentration risk - max position: {max_weight:.1%}")
                            rebalancing_needed = True
        
        if rebalancing_needed:
            decision = "REBALANCE_REQUIRED"
            confidence = 0.80
            reasoning = f"Portfolio optimization needed. {'; '.join(optimization_signals)}"
        else:
            decision = "PORTFOLIO_OPTIMAL"
            confidence = 0.75
            reasoning = f"Portfolio allocation appears well-balanced. {'; '.join(optimization_signals)}"
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'supporting_data': {
                'signals': optimization_signals,
                'rebalancing_needed': rebalancing_needed
            }
        }
    
    def _sentiment_analyst_analysis(self, portfolio_data: Dict[str, Any], 
                                  predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Sentiment analyst specific analysis"""
        sentiment_scores = []
        sentiment_factors = []
        
        for model_name, prediction in predictions.items():
            if 'sentiment' in model_name.lower():
                if isinstance(prediction, dict):
                    sentiment_score = prediction.get('sentiment_score', 0.5)
                    sentiment_scores.append(sentiment_score)
                    
                    if sentiment_score > 0.7:
                        sentiment_factors.append(f"{model_name}: Bullish sentiment")
                    elif sentiment_score < 0.3:
                        sentiment_factors.append(f"{model_name}: Bearish sentiment")
                    else:
                        sentiment_factors.append(f"{model_name}: Neutral sentiment")
        
        avg_sentiment = np.mean(sentiment_scores) if sentiment_scores else 0.5
        
        if avg_sentiment > 0.7:
            decision = "BULLISH_SENTIMENT"
            confidence = 0.75
            reasoning = f"Strong positive market sentiment. {'; '.join(sentiment_factors)}"
        elif avg_sentiment < 0.3:
            decision = "BEARISH_SENTIMENT"
            confidence = 0.75
            reasoning = f"Negative market sentiment detected. {'; '.join(sentiment_factors)}"
        else:
            decision = "NEUTRAL_SENTIMENT"
            confidence = 0.65
            reasoning = f"Mixed or neutral market sentiment. {'; '.join(sentiment_factors)}"
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'supporting_data': {
                'sentiment_scores': sentiment_scores,
                'avg_sentiment': avg_sentiment,
                'factors': sentiment_factors
            }
        }
    
    def _technical_analyst_analysis(self, portfolio_data: Dict[str, Any], 
                                  predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Technical analyst specific analysis"""
        technical_signals = []
        momentum_indicators = []
        
        for model_name, prediction in predictions.items():
            if any(term in model_name.lower() for term in ['momentum', 'technical', 'trend', 'anomaly']):
                if isinstance(prediction, dict):
                    direction = prediction.get('direction', 'neutral')
                    strength = prediction.get('strength', 'weak')
                    
                    if direction == 'bullish' and strength == 'strong':
                        technical_signals.append(f"Strong bullish momentum ({model_name})")
                        momentum_indicators.append(1)
                    elif direction == 'bearish' and strength == 'strong':
                        technical_signals.append(f"Strong bearish momentum ({model_name})")
                        momentum_indicators.append(-1)
                    else:
                        technical_signals.append(f"Neutral/weak signals ({model_name})")
                        momentum_indicators.append(0)
        
        avg_momentum = np.mean(momentum_indicators) if momentum_indicators else 0
        
        if avg_momentum > 0.5:
            decision = "BULLISH_TECHNICAL"
            confidence = 0.80
            reasoning = f"Technical indicators showing bullish signals. {'; '.join(technical_signals)}"
        elif avg_momentum < -0.5:
            decision = "BEARISH_TECHNICAL"
            confidence = 0.80
            reasoning = f"Technical indicators showing bearish signals. {'; '.join(technical_signals)}"
        else:
            decision = "NEUTRAL_TECHNICAL"
            confidence = 0.60
            reasoning = f"Mixed technical signals. {'; '.join(technical_signals)}"
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'supporting_data': {
                'signals': technical_signals,
                'momentum_score': avg_momentum
            }
        }
    
    def _volatility_expert_analysis(self, portfolio_data: Dict[str, Any], 
                                  predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Volatility expert specific analysis"""
        volatility_forecasts = []
        volatility_alerts = []
        
        for model_name, prediction in predictions.items():
            if 'volatility' in model_name.lower():
                if isinstance(prediction, dict):
                    current_vol = prediction.get('current_volatility', 0.2)
                    forecast_vol = prediction.get('forecast_volatility', 0.2)
                    
                    volatility_forecasts.append(forecast_vol)
                    
                    vol_change = (forecast_vol - current_vol) / current_vol if current_vol > 0 else 0
                    
                    if vol_change > 0.2:
                        volatility_alerts.append(f"Volatility surge expected: +{vol_change:.1%}")
                    elif vol_change < -0.2:
                        volatility_alerts.append(f"Volatility decline expected: {vol_change:.1%}")
        
        avg_forecast_vol = np.mean(volatility_forecasts) if volatility_forecasts else 0.2
        
        if avg_forecast_vol > 0.3:
            decision = "HIGH_VOLATILITY_AHEAD"
            confidence = 0.75
            reasoning = f"High volatility environment expected. {'; '.join(volatility_alerts)}"
        elif avg_forecast_vol < 0.15:
            decision = "LOW_VOLATILITY_AHEAD"
            confidence = 0.70
            reasoning = f"Low volatility environment expected. {'; '.join(volatility_alerts)}"
        else:
            decision = "NORMAL_VOLATILITY"
            confidence = 0.65
            reasoning = f"Normal volatility levels expected. {'; '.join(volatility_alerts)}"
        
        return {
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            'supporting_data': {
                'forecast_volatility': avg_forecast_vol,
                'alerts': volatility_alerts
            }
        }
    
    def _generic_analysis(self, portfolio_data: Dict[str, Any], 
                        predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Generic analysis for unspecified roles"""
        return {
            'decision': 'ANALYSIS_COMPLETE',
            'confidence': 0.60,
            'reasoning': f'Completed analysis with {len(predictions)} model predictions',
            'supporting_data': {'prediction_count': len(predictions)}
        }
    
    def _create_error_decision(self, error_message: str) -> AgentDecision:
        """Create error decision when analysis fails"""
        return AgentDecision(
            agent_id=self.agent_id,
            role=self.role,
            decision="ERROR",
            confidence=0.0,
            reasoning=f"Analysis failed: {error_message}",
            supporting_data={'error': error_message},
            timestamp=datetime.now(),
            model_predictions={}
        )

class AgenticAIEnsemble:
    """Main Agentic AI Ensemble System"""
    
    def __init__(self, rimsi_model_registry=None):
        self.model_registry = rimsi_model_registry
        self.agents = {}
        self.coordinator_agent = None
        self.analysis_history = []
        self.performance_tracker = defaultdict(list)
    
    def create_ensemble(self, selected_models: List[str], agent_mode: AgentMode = AgentMode.COLLABORATIVE) -> Dict[str, Any]:
        """Create AI ensemble from selected ML models"""
        try:
            # Clear existing agents
            self.agents = {}
            
            # Assign models to agents based on their type
            model_assignments = self._assign_models_to_agents(selected_models)
            
            # Create agents
            for role, models in model_assignments.items():
                if models:  # Only create agent if it has models
                    agent_id = f"{role.value}_agent"
                    agent = AgenticMLAgent(
                        agent_id=agent_id,
                        role=role,
                        assigned_models=models,
                        rimsi_model_registry=self.model_registry
                    )
                    self.agents[agent_id] = agent
            
            # Create coordinator agent
            coordinator_models = selected_models[:3]  # Give coordinator access to top models
            self.coordinator_agent = AgenticMLAgent(
                agent_id="coordinator",
                role=AgentRole.COORDINATOR,
                assigned_models=coordinator_models,
                rimsi_model_registry=self.model_registry
            )
            
            logger.info(f"Created ensemble with {len(self.agents)} specialized agents")
            
            return {
                'success': True,
                'ensemble_id': f"ensemble_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'agents_created': len(self.agents),
                'agent_roles': [agent.role.value for agent in self.agents.values()],
                'model_assignments': {role.value: models for role, models in model_assignments.items()},
                'mode': agent_mode.value
            }
            
        except Exception as e:
            logger.error(f"Error creating ensemble: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _assign_models_to_agents(self, selected_models: List[str]) -> Dict[AgentRole, List[str]]:
        """Assign ML models to appropriate agent roles"""
        assignments = defaultdict(list)
        
        for model_name in selected_models:
            model_name_lower = model_name.lower()
            
            # Risk-related models
            if any(term in model_name_lower for term in ['risk', 'var', 'tail', 'stress']):
                assignments[AgentRole.RISK_MANAGER].append(model_name)
            
            # Portfolio optimization models
            elif any(term in model_name_lower for term in ['portfolio', 'optimization', 'allocation', 'factor']):
                assignments[AgentRole.PORTFOLIO_OPTIMIZER].append(model_name)
            
            # Sentiment models
            elif any(term in model_name_lower for term in ['sentiment', 'news', 'social', 'options']):
                assignments[AgentRole.SENTIMENT_ANALYST].append(model_name)
            
            # Technical analysis models
            elif any(term in model_name_lower for term in ['momentum', 'technical', 'trend', 'anomaly', 'reversion']):
                assignments[AgentRole.TECHNICAL_ANALYST].append(model_name)
            
            # Volatility models
            elif any(term in model_name_lower for term in ['volatility', 'vol', 'garch']):
                assignments[AgentRole.VOLATILITY_EXPERT].append(model_name)
            
            # Price prediction models
            elif any(term in model_name_lower for term in ['price', 'microstructure']):
                assignments[AgentRole.TECHNICAL_ANALYST].append(model_name)
            
            # Default assignment
            else:
                assignments[AgentRole.TECHNICAL_ANALYST].append(model_name)
        
        return dict(assignments)
    
    async def analyze_portfolio(self, portfolio_data: Dict[str, Any], 
                              analysis_depth: str = "standard") -> Dict[str, Any]:
        """Perform comprehensive portfolio analysis using AI ensemble"""
        try:
            if not self.agents:
                return {
                    'success': False,
                    'error': 'No agents available. Please create ensemble first.'
                }
            
            # Prepare market data (mock for now)
            market_data = self._prepare_market_data(portfolio_data)
            
            # Run agent analyses in parallel
            agent_decisions = await self._run_parallel_analysis(portfolio_data, market_data)
            
            # Generate ensemble insights
            ensemble_insights = self._generate_ensemble_insights(agent_decisions, analysis_depth)
            
            # Create final analysis result
            analysis_result = {
                'success': True,
                'analysis_id': f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'portfolio_id': portfolio_data.get('portfolio_id'),
                'timestamp': datetime.now().isoformat(),
                'agent_decisions': [self._serialize_decision(d) for d in agent_decisions],
                'ensemble_insights': [self._serialize_insight(i) for i in ensemble_insights],
                'summary': self._create_analysis_summary(agent_decisions, ensemble_insights),
                'recommendations': self._generate_recommendations(ensemble_insights),
                'confidence_score': self._calculate_ensemble_confidence(agent_decisions)
            }
            
            # Store analysis history
            self.analysis_history.append(analysis_result)
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in ensemble analysis: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_market_data(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare market data for analysis"""
        return {
            'market_regime': 'normal',
            'volatility_regime': 'moderate',
            'economic_indicators': {
                'interest_rates': 'rising',
                'inflation': 'moderate',
                'gdp_growth': 'positive'
            },
            'market_sentiment': 'neutral'
        }
    
    async def _run_parallel_analysis(self, portfolio_data: Dict[str, Any], 
                                   market_data: Dict[str, Any]) -> List[AgentDecision]:
        """Run agent analyses in parallel"""
        
        async def run_agent_analysis(agent):
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                return await loop.run_in_executor(
                    executor, 
                    agent.analyze_portfolio, 
                    portfolio_data, 
                    market_data
                )
        
        # Create tasks for all agents
        tasks = [run_agent_analysis(agent) for agent in self.agents.values()]
        
        # Run analyses in parallel
        agent_decisions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid decisions
        valid_decisions = []
        for i, result in enumerate(agent_decisions):
            if isinstance(result, Exception):
                logger.error(f"Agent analysis failed: {result}")
            elif isinstance(result, AgentDecision):
                valid_decisions.append(result)
        
        return valid_decisions
    
    def _generate_ensemble_insights(self, agent_decisions: List[AgentDecision], 
                                  analysis_depth: str) -> List[EnsembleInsight]:
        """Generate insights from agent decisions"""
        insights = []
        
        # Group decisions by type
        decision_groups = defaultdict(list)
        for decision in agent_decisions:
            decision_groups[decision.decision].append(decision)
        
        # Risk insights
        risk_decisions = [d for d in agent_decisions if 'RISK' in d.decision]
        if risk_decisions:
            insight = self._create_risk_insight(risk_decisions)
            if insight:
                insights.append(insight)
        
        # Portfolio optimization insights
        optimization_decisions = [d for d in agent_decisions if 'PORTFOLIO' in d.decision or 'REBALANCE' in d.decision]
        if optimization_decisions:
            insight = self._create_optimization_insight(optimization_decisions)
            if insight:
                insights.append(insight)
        
        # Technical analysis insights
        technical_decisions = [d for d in agent_decisions if 'TECHNICAL' in d.decision]
        if technical_decisions:
            insight = self._create_technical_insight(technical_decisions)
            if insight:
                insights.append(insight)
        
        # Sentiment insights
        sentiment_decisions = [d for d in agent_decisions if 'SENTIMENT' in d.decision]
        if sentiment_decisions:
            insight = self._create_sentiment_insight(sentiment_decisions)
            if insight:
                insights.append(insight)
        
        # Volatility insights
        volatility_decisions = [d for d in agent_decisions if 'VOLATILITY' in d.decision]
        if volatility_decisions:
            insight = self._create_volatility_insight(volatility_decisions)
            if insight:
                insights.append(insight)
        
        return insights
    
    def _create_risk_insight(self, risk_decisions: List[AgentDecision]) -> Optional[EnsembleInsight]:
        """Create risk-related ensemble insight"""
        if not risk_decisions:
            return None
        
        high_risk_count = sum(1 for d in risk_decisions if 'HIGH_RISK' in d.decision)
        avg_confidence = np.mean([d.confidence for d in risk_decisions])
        
        if high_risk_count > 0:
            severity = "high" if high_risk_count > len(risk_decisions) / 2 else "medium"
            title = "Portfolio Risk Alert"
            description = f"{high_risk_count} out of {len(risk_decisions)} risk agents detected elevated risk levels"
            recommendation = "Consider reducing position sizes or implementing hedging strategies"
        else:
            severity = "low"
            title = "Risk Assessment: Acceptable Levels"
            description = "Risk management agents indicate acceptable portfolio risk levels"
            recommendation = "Current risk profile appears manageable, continue monitoring"
        
        return EnsembleInsight(
            insight_type="risk_assessment",
            title=title,
            description=description,
            confidence=avg_confidence,
            severity=severity,
            recommendation=recommendation,
            supporting_agents=[d.agent_id for d in risk_decisions],
            conflicting_agents=[],
            data_sources=['risk_models', 'var_analysis'],
            timestamp=datetime.now()
        )
    
    def _create_optimization_insight(self, optimization_decisions: List[AgentDecision]) -> Optional[EnsembleInsight]:
        """Create portfolio optimization insight"""
        if not optimization_decisions:
            return None
        
        rebalance_needed = sum(1 for d in optimization_decisions if 'REBALANCE' in d.decision)
        avg_confidence = np.mean([d.confidence for d in optimization_decisions])
        
        if rebalance_needed > 0:
            severity = "medium"
            title = "Portfolio Rebalancing Recommended"
            description = f"Portfolio optimization analysis suggests rebalancing opportunities"
            recommendation = "Consider rebalancing portfolio allocation to improve risk-adjusted returns"
        else:
            severity = "low"
            title = "Portfolio Allocation: Well Balanced"
            description = "Portfolio optimization agents indicate current allocation is appropriate"
            recommendation = "Maintain current allocation, monitor for changes in market conditions"
        
        return EnsembleInsight(
            insight_type="portfolio_optimization",
            title=title,
            description=description,
            confidence=avg_confidence,
            severity=severity,
            recommendation=recommendation,
            supporting_agents=[d.agent_id for d in optimization_decisions],
            conflicting_agents=[],
            data_sources=['portfolio_optimization', 'factor_models'],
            timestamp=datetime.now()
        )
    
    def _create_technical_insight(self, technical_decisions: List[AgentDecision]) -> Optional[EnsembleInsight]:
        """Create technical analysis insight"""
        if not technical_decisions:
            return None
        
        bullish_signals = sum(1 for d in technical_decisions if 'BULLISH' in d.decision)
        bearish_signals = sum(1 for d in technical_decisions if 'BEARISH' in d.decision)
        avg_confidence = np.mean([d.confidence for d in technical_decisions])
        
        if bullish_signals > bearish_signals:
            severity = "low"
            title = "Technical Analysis: Bullish Signals"
            description = f"Technical indicators showing {bullish_signals} bullish vs {bearish_signals} bearish signals"
            recommendation = "Technical conditions support maintaining or increasing positions"
        elif bearish_signals > bullish_signals:
            severity = "medium"
            title = "Technical Analysis: Bearish Signals"
            description = f"Technical indicators showing {bearish_signals} bearish vs {bullish_signals} bullish signals"
            recommendation = "Consider reducing exposure or implementing protective strategies"
        else:
            severity = "low"
            title = "Technical Analysis: Mixed Signals"
            description = "Technical indicators showing mixed or neutral signals"
            recommendation = "Monitor technical developments for clearer directional signals"
        
        return EnsembleInsight(
            insight_type="technical_analysis",
            title=title,
            description=description,
            confidence=avg_confidence,
            severity=severity,
            recommendation=recommendation,
            supporting_agents=[d.agent_id for d in technical_decisions],
            conflicting_agents=[],
            data_sources=['technical_indicators', 'momentum_models'],
            timestamp=datetime.now()
        )
    
    def _create_sentiment_insight(self, sentiment_decisions: List[AgentDecision]) -> Optional[EnsembleInsight]:
        """Create sentiment analysis insight"""
        if not sentiment_decisions:
            return None
        
        bullish_sentiment = sum(1 for d in sentiment_decisions if 'BULLISH' in d.decision)
        bearish_sentiment = sum(1 for d in sentiment_decisions if 'BEARISH' in d.decision)
        avg_confidence = np.mean([d.confidence for d in sentiment_decisions])
        
        if bullish_sentiment > bearish_sentiment:
            severity = "low"
            title = "Market Sentiment: Positive"
            description = f"Sentiment analysis shows {bullish_sentiment} positive vs {bearish_sentiment} negative indicators"
            recommendation = "Positive sentiment supports risk-on positioning"
        elif bearish_sentiment > bullish_sentiment:
            severity = "medium"
            title = "Market Sentiment: Negative"
            description = f"Sentiment analysis shows {bearish_sentiment} negative vs {bullish_sentiment} positive indicators"
            recommendation = "Negative sentiment suggests defensive positioning may be prudent"
        else:
            severity = "low"
            title = "Market Sentiment: Neutral"
            description = "Sentiment indicators showing mixed or neutral readings"
            recommendation = "Neutral sentiment allows for balanced portfolio approach"
        
        return EnsembleInsight(
            insight_type="sentiment_analysis",
            title=title,
            description=description,
            confidence=avg_confidence,
            severity=severity,
            recommendation=recommendation,
            supporting_agents=[d.agent_id for d in sentiment_decisions],
            conflicting_agents=[],
            data_sources=['news_sentiment', 'social_sentiment', 'options_flow'],
            timestamp=datetime.now()
        )
    
    def _create_volatility_insight(self, volatility_decisions: List[AgentDecision]) -> Optional[EnsembleInsight]:
        """Create volatility analysis insight"""
        if not volatility_decisions:
            return None
        
        high_vol_expected = sum(1 for d in volatility_decisions if 'HIGH_VOLATILITY' in d.decision)
        avg_confidence = np.mean([d.confidence for d in volatility_decisions])
        
        if high_vol_expected > 0:
            severity = "medium"
            title = "Volatility Outlook: Elevated Levels Expected"
            description = f"Volatility models predicting higher volatility environment"
            recommendation = "Consider reducing position sizes or implementing volatility hedging"
        else:
            severity = "low"
            title = "Volatility Outlook: Stable Environment"
            description = "Volatility models suggest stable to declining volatility"
            recommendation = "Lower volatility environment may support larger position sizes"
        
        return EnsembleInsight(
            insight_type="volatility_analysis",
            title=title,
            description=description,
            confidence=avg_confidence,
            severity=severity,
            recommendation=recommendation,
            supporting_agents=[d.agent_id for d in volatility_decisions],
            conflicting_agents=[],
            data_sources=['volatility_models', 'garch_forecasts'],
            timestamp=datetime.now()
        )
    
    def _create_analysis_summary(self, agent_decisions: List[AgentDecision], 
                               ensemble_insights: List[EnsembleInsight]) -> Dict[str, Any]:
        """Create analysis summary"""
        return {
            'total_agents': len(agent_decisions),
            'total_insights': len(ensemble_insights),
            'high_severity_insights': len([i for i in ensemble_insights if i.severity == 'high']),
            'avg_confidence': np.mean([d.confidence for d in agent_decisions]) if agent_decisions else 0.0,
            'consensus_level': self._calculate_consensus_level(agent_decisions),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, insights: List[EnsembleInsight]) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        for insight in insights:
            if insight.severity == 'high':
                priority = 'immediate'
            elif insight.severity == 'medium':
                priority = 'high'
            else:
                priority = 'normal'
            
            recommendations.append({
                'priority': priority,
                'action': insight.recommendation,
                'rationale': insight.description,
                'confidence': insight.confidence,
                'insight_type': insight.insight_type
            })
        
        # Sort by priority and confidence
        priority_order = {'immediate': 3, 'high': 2, 'normal': 1}
        recommendations.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['confidence']), reverse=True)
        
        return recommendations
    
    def _calculate_ensemble_confidence(self, agent_decisions: List[AgentDecision]) -> float:
        """Calculate overall ensemble confidence"""
        if not agent_decisions:
            return 0.0
        
        confidences = [d.confidence for d in agent_decisions]
        return float(np.mean(confidences))
    
    def _calculate_consensus_level(self, agent_decisions: List[AgentDecision]) -> float:
        """Calculate consensus level among agents"""
        if len(agent_decisions) < 2:
            return 1.0
        
        # Group decisions and calculate consensus
        decision_counts = defaultdict(int)
        for decision in agent_decisions:
            decision_counts[decision.decision] += 1
        
        max_consensus = max(decision_counts.values())
        consensus_level = max_consensus / len(agent_decisions)
        
        return float(consensus_level)
    
    def _serialize_decision(self, decision: AgentDecision) -> Dict[str, Any]:
        """Serialize agent decision for JSON response"""
        return {
            'agent_id': decision.agent_id,
            'role': decision.role.value,
            'decision': decision.decision,
            'confidence': decision.confidence,
            'reasoning': decision.reasoning,
            'supporting_data': decision.supporting_data,
            'timestamp': decision.timestamp.isoformat(),
            'model_predictions_count': len(decision.model_predictions)
        }
    
    def _serialize_insight(self, insight: EnsembleInsight) -> Dict[str, Any]:
        """Serialize ensemble insight for JSON response"""
        return {
            'insight_type': insight.insight_type,
            'title': insight.title,
            'description': insight.description,
            'confidence': insight.confidence,
            'severity': insight.severity,
            'recommendation': insight.recommendation,
            'supporting_agents': insight.supporting_agents,
            'conflicting_agents': insight.conflicting_agents,
            'data_sources': insight.data_sources,
            'timestamp': insight.timestamp.isoformat()
        }

# Global agentic AI instance
agentic_ai_ensemble = None

def initialize_agentic_ai(rimsi_model_registry=None):
    """Initialize the global agentic AI ensemble"""
    global agentic_ai_ensemble
    agentic_ai_ensemble = AgenticAIEnsemble(rimsi_model_registry)
    logger.info("Agentic AI Ensemble initialized successfully")
    return agentic_ai_ensemble

def get_agentic_ai_ensemble():
    """Get the global agentic AI ensemble instance"""
    return agentic_ai_ensemble