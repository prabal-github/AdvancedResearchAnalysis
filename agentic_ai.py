#!/usr/bin/env python3
"""
Agentic AI Implementation for Investment Advisory
Built on top of existing Research Quality Assessment System

This module implements autonomous AI agents that can:
1. Analyze research reports and make investment decisions
2. Learn from outcomes and adapt strategies
3. Provide personalized recommendations
4. Monitor markets and act proactively
"""

import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Import existing models (assuming they're available)
try:
    from app import db, Report, AnalystPerformanceMetrics, InvestorAccount, KnowledgeBase
except ImportError:
    print("Note: Import app models when integrating with main system")

class InvestmentAgent:
    """Core AI agent for autonomous investment advisory"""
    
    def __init__(self, investor_id: str, config: Dict = None):
        self.investor_id = investor_id
        self.config = config or self._default_config()
        self.decision_engine = DecisionEngine()
        self.research_analyzer = ResearchAnalyzer()
        self.learning_system = LearningSystem()
        self.risk_manager = RiskManager()
        
        # Load investor profile
        self.investor_profile = self._load_investor_profile()
        
        # Initialize performance tracking
        self.performance_tracker = PerformanceTracker(investor_id)
        
        logging.info(f"Investment Agent initialized for investor {investor_id}")
    
    def _default_config(self) -> Dict:
        """Default agent configuration"""
        return {
            'confidence_threshold': 0.7,
            'risk_tolerance': 0.5,
            'learning_rate': 0.1,
            'max_recommendations_per_day': 5,
            'quality_score_minimum': 0.6,
            'analyst_accuracy_weight': 0.3,
            'market_sentiment_weight': 0.2,
            'research_quality_weight': 0.5
        }
    
    def autonomous_analysis(self) -> Dict:
        """Main autonomous analysis function - runs continuously"""
        try:
            # Step 1: Get latest market data and research
            market_context = self._get_market_context()
            new_research = self._get_new_research()
            
            # Step 2: Filter research by quality (use existing scoring system)
            quality_research = self._filter_by_quality(new_research)
            
            # Step 3: Analyze research for investment opportunities
            opportunities = self.research_analyzer.find_opportunities(
                quality_research, self.investor_profile
            )
            
            # Step 4: Generate recommendations using decision engine
            recommendations = self.decision_engine.generate_recommendations(
                opportunities, market_context, self.investor_profile
            )
            
            # Step 5: Apply risk management
            risk_adjusted_recs = self.risk_manager.apply_risk_filters(
                recommendations, self.investor_profile
            )
            
            # Step 6: Execute high-confidence actions
            actions_taken = self._execute_autonomous_actions(risk_adjusted_recs)
            
            # Step 7: Log all activities
            self._log_agent_activity({
                'opportunities_found': len(opportunities),
                'recommendations_generated': len(recommendations),
                'actions_taken': len(actions_taken),
                'timestamp': datetime.utcnow(),
                'market_context': market_context
            })
            
            return {
                'status': 'success',
                'recommendations': risk_adjusted_recs,
                'actions_taken': actions_taken,
                'market_context': market_context
            }
            
        except Exception as e:
            logging.error(f"Autonomous analysis failed: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def personalized_recommendations(self, query: str = None) -> List[Dict]:
        """Generate personalized investment recommendations"""
        
        # Analyze investor's current portfolio and preferences
        portfolio_analysis = self._analyze_current_portfolio()
        
        # Get investor-specific constraints
        constraints = self._get_investor_constraints()
        
        # Find opportunities matching investor profile
        matching_opportunities = self._find_matching_opportunities(
            portfolio_analysis, constraints, query
        )
        
        # Rank opportunities by expected success
        ranked_opportunities = self._rank_by_expected_success(matching_opportunities)
        
        # Generate detailed recommendations
        recommendations = []
        for opportunity in ranked_opportunities[:self.config['max_recommendations_per_day']]:
            rec = self._create_detailed_recommendation(opportunity)
            recommendations.append(rec)
        
        return recommendations
    
    def learn_from_outcomes(self) -> Dict:
        """Learn from past recommendations and adapt strategies"""
        
        # Get past recommendations and their outcomes
        past_recommendations = self._get_past_recommendations()
        
        learning_data = []
        for rec in past_recommendations:
            outcome = self._measure_recommendation_outcome(rec)
            if outcome:
                learning_pattern = self.learning_system.extract_patterns(rec, outcome)
                learning_data.append(learning_pattern)
        
        # Update agent parameters based on learning
        improvements = self.learning_system.update_agent_parameters(
            learning_data, self.config
        )
        
        # Apply improvements
        self.config.update(improvements)
        
        return {
            'patterns_learned': len(learning_data),
            'parameters_updated': list(improvements.keys()),
            'performance_improvement': improvements.get('performance_delta', 0)
        }
    
    def proactive_monitoring(self) -> List[Dict]:
        """Proactively monitor market and generate alerts"""
        
        alerts = []
        
        # Monitor for significant market events
        market_events = self._detect_market_events()
        for event in market_events:
            if self._affects_investor_portfolio(event):
                alert = self._create_market_alert(event)
                alerts.append(alert)
        
        # Monitor analyst reports for portfolio holdings
        portfolio_tickers = self._get_portfolio_tickers()
        new_research_alerts = self._monitor_research_updates(portfolio_tickers)
        alerts.extend(new_research_alerts)
        
        # Monitor for risk threshold breaches
        risk_alerts = self._monitor_risk_levels()
        alerts.extend(risk_alerts)
        
        return alerts
    
    # Helper methods
    def _load_investor_profile(self) -> Dict:
        """Load investor profile from database"""
        # This would integrate with your existing InvestorAccount model
        return {
            'risk_tolerance': 0.5,
            'investment_horizon': 'medium_term',
            'preferred_sectors': ['technology', 'banking'],
            'investment_style': 'moderate'
        }
    
    def _get_market_context(self) -> Dict:
        """Get current market context and conditions"""
        return {
            'market_trend': 'bullish',  # This would come from real market data
            'volatility': 0.3,
            'sector_performance': {'technology': 0.05, 'banking': -0.02},
            'timestamp': datetime.utcnow()
        }
    
    def _get_new_research(self) -> List[Dict]:
        """Get new research reports since last analysis"""
        # This would integrate with your existing Report model
        # For now, return sample data
        return [
            {
                'id': 'rpt_001',
                'analyst': 'John Doe',
                'ticker': 'TCS.NS',
                'quality_score': 0.85,
                'recommendation': 'BUY',
                'target_price': 4200,
                'created_at': datetime.utcnow()
            }
        ]
    
    def _filter_by_quality(self, research_reports: List[Dict]) -> List[Dict]:
        """Filter research by quality score using existing system"""
        min_quality = self.config['quality_score_minimum']
        return [r for r in research_reports if r.get('quality_score', 0) >= min_quality]
    
    def _execute_autonomous_actions(self, recommendations: List[Dict]) -> List[Dict]:
        """Execute high-confidence autonomous actions"""
        actions = []
        
        for rec in recommendations:
            if rec['confidence'] >= self.config['confidence_threshold']:
                action = {
                    'type': 'recommendation_generated',
                    'ticker': rec['ticker'],
                    'action': rec['recommendation'],
                    'confidence': rec['confidence'],
                    'executed_at': datetime.utcnow()
                }
                actions.append(action)
                # Here you would actually execute the action
                # (notify investor, create alert, etc.)
        
        return actions
    
    def _log_agent_activity(self, activity: Dict):
        """Log agent activity for tracking and debugging"""
        logging.info(f"Agent activity: {json.dumps(activity, default=str)}")


class DecisionEngine:
    """Core decision-making engine for investment recommendations"""
    
    def __init__(self):
        self.decision_weights = {
            'research_quality': 0.4,
            'analyst_track_record': 0.3,
            'market_conditions': 0.2,
            'risk_factors': 0.1
        }
    
    def generate_recommendations(self, opportunities: List[Dict], 
                               market_context: Dict, 
                               investor_profile: Dict) -> List[Dict]:
        """Generate investment recommendations based on opportunities"""
        
        recommendations = []
        
        for opp in opportunities:
            # Calculate recommendation score
            score = self._calculate_recommendation_score(opp, market_context, investor_profile)
            
            # Generate recommendation if score is high enough
            if score['total_score'] > 0.6:
                rec = {
                    'ticker': opp['ticker'],
                    'recommendation': self._determine_recommendation_type(score),
                    'target_price': opp.get('target_price'),
                    'confidence': score['total_score'],
                    'reasoning': score['factors'],
                    'risk_level': self._assess_risk_level(opp, investor_profile),
                    'expected_return': score.get('expected_return', 0),
                    'time_horizon': opp.get('time_horizon', 'medium_term')
                }
                recommendations.append(rec)
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x['confidence'], reverse=True)
        
        return recommendations
    
    def _calculate_recommendation_score(self, opportunity: Dict, 
                                     market_context: Dict, 
                                     investor_profile: Dict) -> Dict:
        """Calculate comprehensive recommendation score"""
        
        factors = {}
        
        # Research quality factor
        factors['research_quality'] = opportunity.get('quality_score', 0.5) * \
                                    self.decision_weights['research_quality']
        
        # Analyst track record factor (would integrate with your existing data)
        analyst_performance = 0.7  # This would come from AnalystPerformanceMetrics
        factors['analyst_track_record'] = analyst_performance * \
                                        self.decision_weights['analyst_track_record']
        
        # Market conditions factor
        market_score = self._evaluate_market_conditions(market_context, opportunity['ticker'])
        factors['market_conditions'] = market_score * self.decision_weights['market_conditions']
        
        # Risk factor assessment
        risk_score = self._evaluate_risk_factors(opportunity, investor_profile)
        factors['risk_factors'] = risk_score * self.decision_weights['risk_factors']
        
        total_score = sum(factors.values())
        
        return {
            'total_score': total_score,
            'factors': factors,
            'expected_return': self._estimate_expected_return(opportunity, factors)
        }
    
    def _determine_recommendation_type(self, score: Dict) -> str:
        """Determine BUY/HOLD/SELL based on score"""
        total_score = score['total_score']
        
        if total_score >= 0.8:
            return 'STRONG_BUY'
        elif total_score >= 0.65:
            return 'BUY'
        elif total_score >= 0.45:
            return 'HOLD'
        elif total_score >= 0.3:
            return 'SELL'
        else:
            return 'STRONG_SELL'
    
    def _evaluate_market_conditions(self, market_context: Dict, ticker: str) -> float:
        """Evaluate how market conditions affect the ticker"""
        # Simple implementation - would be more sophisticated in practice
        market_trend_score = 0.7 if market_context.get('market_trend') == 'bullish' else 0.3
        volatility_score = 1 - market_context.get('volatility', 0.5)
        
        return (market_trend_score + volatility_score) / 2
    
    def _evaluate_risk_factors(self, opportunity: Dict, investor_profile: Dict) -> float:
        """Evaluate risk factors against investor profile"""
        # Risk assessment based on investor tolerance
        risk_tolerance = investor_profile.get('risk_tolerance', 0.5)
        opportunity_risk = opportunity.get('risk_level', 0.5)
        
        # Return higher score if risk matches investor tolerance
        risk_match_score = 1 - abs(risk_tolerance - opportunity_risk)
        
        return risk_match_score
    
    def _assess_risk_level(self, opportunity: Dict, investor_profile: Dict) -> str:
        """Assess risk level for the opportunity"""
        risk_score = opportunity.get('risk_level', 0.5)
        
        if risk_score <= 0.3:
            return 'LOW'
        elif risk_score <= 0.6:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _estimate_expected_return(self, opportunity: Dict, factors: Dict) -> float:
        """Estimate expected return based on factors"""
        base_return = 0.12  # Base expected annual return
        quality_multiplier = factors.get('research_quality', 0) * 2
        analyst_multiplier = factors.get('analyst_track_record', 0) * 1.5
        
        estimated_return = base_return * (1 + quality_multiplier + analyst_multiplier)
        return min(estimated_return, 0.5)  # Cap at 50% annual return


class ResearchAnalyzer:
    """Analyzes research reports to find investment opportunities"""
    
    def find_opportunities(self, research_reports: List[Dict], 
                          investor_profile: Dict) -> List[Dict]:
        """Find investment opportunities from research reports"""
        
        opportunities = []
        
        for report in research_reports:
            # Extract key information from report
            opportunity = self._extract_opportunity(report)
            
            # Check if it matches investor profile
            if self._matches_investor_profile(opportunity, investor_profile):
                # Enrich with additional analysis
                enriched_opportunity = self._enrich_opportunity(opportunity)
                opportunities.append(enriched_opportunity)
        
        return opportunities
    
    def _extract_opportunity(self, report: Dict) -> Dict:
        """Extract opportunity information from research report"""
        return {
            'ticker': report.get('ticker'),
            'recommendation': report.get('recommendation'),
            'target_price': report.get('target_price'),
            'quality_score': report.get('quality_score'),
            'analyst': report.get('analyst'),
            'sector': report.get('sector', 'unknown'),
            'risk_level': self._estimate_risk_level(report),
            'time_horizon': report.get('time_horizon', 'medium_term'),
            'report_id': report.get('id')
        }
    
    def _matches_investor_profile(self, opportunity: Dict, profile: Dict) -> bool:
        """Check if opportunity matches investor profile"""
        
        # Check sector preference
        preferred_sectors = profile.get('preferred_sectors', [])
        if preferred_sectors and opportunity.get('sector') not in preferred_sectors:
            return False
        
        # Check risk tolerance
        risk_tolerance = profile.get('risk_tolerance', 0.5)
        opportunity_risk = opportunity.get('risk_level', 0.5)
        if abs(risk_tolerance - opportunity_risk) > 0.3:
            return False
        
        # Check investment horizon
        investor_horizon = profile.get('investment_horizon', 'medium_term')
        opp_horizon = opportunity.get('time_horizon', 'medium_term')
        if investor_horizon != opp_horizon and investor_horizon != 'flexible':
            return False
        
        return True
    
    def _enrich_opportunity(self, opportunity: Dict) -> Dict:
        """Enrich opportunity with additional analysis"""
        # Add technical indicators, sector analysis, etc.
        opportunity['technical_score'] = self._calculate_technical_score(opportunity['ticker'])
        opportunity['sector_momentum'] = self._get_sector_momentum(opportunity['sector'])
        opportunity['peer_comparison'] = self._get_peer_comparison(opportunity['ticker'])
        
        return opportunity
    
    def _estimate_risk_level(self, report: Dict) -> float:
        """Estimate risk level from report data"""
        # Simple risk estimation - would be more sophisticated in practice
        quality_score = report.get('quality_score', 0.5)
        
        # Higher quality research typically means lower risk
        risk_level = 1 - (quality_score * 0.6)  # Inverse relationship
        
        return max(0.1, min(0.9, risk_level))  # Keep within bounds
    
    def _calculate_technical_score(self, ticker: str) -> float:
        """Calculate technical analysis score"""
        # This would integrate with technical analysis tools
        return random.uniform(0.3, 0.9)  # Placeholder
    
    def _get_sector_momentum(self, sector: str) -> float:
        """Get sector momentum score"""
        # This would analyze sector performance trends
        return random.uniform(0.2, 0.8)  # Placeholder
    
    def _get_peer_comparison(self, ticker: str) -> Dict:
        """Get peer comparison data"""
        return {
            'vs_sector_avg': random.uniform(-0.1, 0.1),
            'vs_market': random.uniform(-0.05, 0.05),
            'rank_in_sector': random.randint(1, 10)
        }


class LearningSystem:
    """System for learning from outcomes and improving decisions"""
    
    def extract_patterns(self, recommendation: Dict, outcome: Dict) -> Dict:
        """Extract learning patterns from recommendation outcomes"""
        
        success = outcome.get('success', False)
        return_achieved = outcome.get('return', 0)
        
        pattern = {
            'analyst': recommendation.get('analyst'),
            'sector': recommendation.get('sector'),
            'recommendation_type': recommendation.get('recommendation'),
            'confidence_level': recommendation.get('confidence'),
            'market_conditions': outcome.get('market_conditions', {}),
            'success': success,
            'return_achieved': return_achieved,
            'factors_that_worked': [],
            'factors_that_failed': [],
            'timestamp': datetime.utcnow()
        }
        
        # Analyze which factors contributed to success/failure
        if success:
            pattern['factors_that_worked'] = self._identify_success_factors(recommendation, outcome)
        else:
            pattern['factors_that_failed'] = self._identify_failure_factors(recommendation, outcome)
        
        return pattern
    
    def update_agent_parameters(self, learning_data: List[Dict], current_config: Dict) -> Dict:
        """Update agent parameters based on learning data"""
        
        improvements = {}
        
        # Analyze success patterns
        success_patterns = [ld for ld in learning_data if ld['success']]
        failure_patterns = [ld for ld in learning_data if not ld['success']]
        
        # Adjust confidence threshold
        if len(success_patterns) > 0:
            avg_success_confidence = sum(sp['confidence_level'] for sp in success_patterns) / len(success_patterns)
            if len(failure_patterns) > 0:
                avg_failure_confidence = sum(fp['confidence_level'] for fp in failure_patterns) / len(failure_patterns)
                
                # If successful recommendations had higher confidence, raise threshold
                if avg_success_confidence > avg_failure_confidence:
                    new_threshold = min(0.9, current_config['confidence_threshold'] + 0.05)
                    improvements['confidence_threshold'] = new_threshold
        
        # Adjust sector weights based on performance
        sector_performance = self._analyze_sector_performance(learning_data)
        if sector_performance:
            improvements['sector_weights'] = sector_performance
        
        # Calculate performance improvement
        if learning_data:
            recent_success_rate = sum(ld['success'] for ld in learning_data[-10:]) / min(10, len(learning_data))
            improvements['performance_delta'] = recent_success_rate - 0.5  # Assuming 50% baseline
        
        return improvements
    
    def _identify_success_factors(self, recommendation: Dict, outcome: Dict) -> List[str]:
        """Identify factors that contributed to success"""
        factors = []
        
        if recommendation.get('confidence', 0) > 0.8:
            factors.append('high_confidence')
        
        if recommendation.get('quality_score', 0) > 0.7:
            factors.append('high_quality_research')
        
        if outcome.get('market_conditions', {}).get('trend') == 'bullish':
            factors.append('favorable_market')
        
        return factors
    
    def _identify_failure_factors(self, recommendation: Dict, outcome: Dict) -> List[str]:
        """Identify factors that contributed to failure"""
        factors = []
        
        if recommendation.get('confidence', 0) < 0.6:
            factors.append('low_confidence')
        
        if recommendation.get('quality_score', 0) < 0.5:
            factors.append('poor_quality_research')
        
        if outcome.get('market_conditions', {}).get('volatility', 0) > 0.5:
            factors.append('high_volatility')
        
        return factors
    
    def _analyze_sector_performance(self, learning_data: List[Dict]) -> Dict:
        """Analyze performance by sector"""
        sector_stats = {}
        
        for data in learning_data:
            sector = data.get('sector')
            if sector:
                if sector not in sector_stats:
                    sector_stats[sector] = {'total': 0, 'successful': 0}
                
                sector_stats[sector]['total'] += 1
                if data['success']:
                    sector_stats[sector]['successful'] += 1
        
        # Calculate success rates
        sector_performance = {}
        for sector, stats in sector_stats.items():
            if stats['total'] > 0:
                success_rate = stats['successful'] / stats['total']
                sector_performance[sector] = success_rate
        
        return sector_performance


class RiskManager:
    """Risk management system for investment recommendations"""
    
    def __init__(self):
        self.risk_limits = {
            'max_portfolio_concentration': 0.1,  # Max 10% in single stock
            'max_sector_exposure': 0.3,          # Max 30% in single sector
            'max_daily_recommendations': 5,       # Max 5 recommendations per day
            'min_diversification_score': 0.6     # Minimum diversification score
        }
    
    def apply_risk_filters(self, recommendations: List[Dict], 
                          investor_profile: Dict) -> List[Dict]:
        """Apply risk management filters to recommendations"""
        
        filtered_recs = []
        risk_tolerance = investor_profile.get('risk_tolerance', 0.5)
        
        for rec in recommendations:
            # Check risk level against investor tolerance
            if self._check_risk_tolerance(rec, risk_tolerance):
                # Check position sizing
                if self._check_position_sizing(rec, investor_profile):
                    # Check diversification
                    if self._check_diversification(rec, filtered_recs):
                        filtered_recs.append(rec)
        
        # Limit number of recommendations
        return filtered_recs[:self.risk_limits['max_daily_recommendations']]
    
    def _check_risk_tolerance(self, recommendation: Dict, risk_tolerance: float) -> bool:
        """Check if recommendation matches investor's risk tolerance"""
        rec_risk = self._map_risk_level_to_score(recommendation.get('risk_level', 'MEDIUM'))
        
        # Allow some flexibility in risk matching
        tolerance_range = 0.2
        return abs(rec_risk - risk_tolerance) <= tolerance_range
    
    def _check_position_sizing(self, recommendation: Dict, investor_profile: Dict) -> bool:
        """Check position sizing constraints"""
        # This would check against current portfolio
        # For now, always return True
        return True
    
    def _check_diversification(self, recommendation: Dict, existing_recs: List[Dict]) -> bool:
        """Check diversification constraints"""
        rec_sector = recommendation.get('sector', 'unknown')
        
        # Count existing recommendations in same sector
        same_sector_count = sum(1 for rec in existing_recs if rec.get('sector') == rec_sector)
        
        # Don't exceed sector concentration limit
        max_same_sector = int(self.risk_limits['max_daily_recommendations'] * 
                             self.risk_limits['max_sector_exposure'])
        
        return same_sector_count < max_same_sector
    
    def _map_risk_level_to_score(self, risk_level: str) -> float:
        """Map risk level string to numerical score"""
        mapping = {
            'LOW': 0.2,
            'MEDIUM': 0.5,
            'HIGH': 0.8
        }
        return mapping.get(risk_level, 0.5)


class PerformanceTracker:
    """Track agent performance and outcomes"""
    
    def __init__(self, investor_id: str):
        self.investor_id = investor_id
        self.metrics = {
            'total_recommendations': 0,
            'successful_recommendations': 0,
            'total_return': 0.0,
            'accuracy_rate': 0.0,
            'last_updated': datetime.utcnow()
        }
    
    def track_recommendation_outcome(self, recommendation_id: str, outcome: Dict):
        """Track the outcome of a specific recommendation"""
        
        success = outcome.get('success', False)
        return_achieved = outcome.get('return', 0.0)
        
        # Update metrics
        self.metrics['total_recommendations'] += 1
        if success:
            self.metrics['successful_recommendations'] += 1
        
        self.metrics['total_return'] += return_achieved
        self.metrics['accuracy_rate'] = (
            self.metrics['successful_recommendations'] / 
            self.metrics['total_recommendations']
        )
        self.metrics['last_updated'] = datetime.utcnow()
        
        # Here you would save to database
        self._save_metrics()
    
    def get_performance_summary(self) -> Dict:
        """Get performance summary for the agent"""
        return {
            'investor_id': self.investor_id,
            'accuracy_rate': self.metrics['accuracy_rate'],
            'total_recommendations': self.metrics['total_recommendations'],
            'average_return': self.metrics['total_return'] / max(1, self.metrics['total_recommendations']),
            'last_updated': self.metrics['last_updated']
        }
    
    def _save_metrics(self):
        """Save metrics to database"""
        # This would integrate with your database
        logging.info(f"Performance metrics updated for investor {self.investor_id}")


# Main Agent Manager
class AgentManager:
    """Manages multiple AI agents for different investors"""
    
    def __init__(self):
        self.active_agents = {}
        self.agent_configs = {}
    
    def create_agent_for_investor(self, investor_id: str, config: Dict = None) -> InvestmentAgent:
        """Create and configure an AI agent for an investor"""
        
        agent = InvestmentAgent(investor_id, config)
        self.active_agents[investor_id] = agent
        self.agent_configs[investor_id] = config or agent.config
        
        logging.info(f"Created AI agent for investor {investor_id}")
        return agent
    
    def run_all_agents(self):
        """Run autonomous analysis for all active agents"""
        
        results = {}
        
        for investor_id, agent in self.active_agents.items():
            try:
                result = agent.autonomous_analysis()
                results[investor_id] = result
                
                # Also run learning process
                learning_result = agent.learn_from_outcomes()
                results[investor_id]['learning'] = learning_result
                
            except Exception as e:
                logging.error(f"Error running agent for investor {investor_id}: {e}")
                results[investor_id] = {'status': 'error', 'message': str(e)}
        
        return results
    
    def get_agent_for_investor(self, investor_id: str) -> Optional[InvestmentAgent]:
        """Get the AI agent for a specific investor"""
        return self.active_agents.get(investor_id)
    
    def update_agent_config(self, investor_id: str, config_updates: Dict):
        """Update configuration for a specific agent"""
        if investor_id in self.active_agents:
            agent = self.active_agents[investor_id]
            agent.config.update(config_updates)
            self.agent_configs[investor_id].update(config_updates)
            
            logging.info(f"Updated config for agent {investor_id}: {config_updates}")


# Example usage and testing
if __name__ == "__main__":
    # Initialize logging
    logging.basicConfig(level=logging.INFO)
    
    # Create agent manager
    manager = AgentManager()
    
    # Create a sample agent
    sample_config = {
        'confidence_threshold': 0.75,
        'risk_tolerance': 0.6,
        'preferred_sectors': ['technology', 'banking']
    }
    
    agent = manager.create_agent_for_investor('investor_001', sample_config)
    
    # Run autonomous analysis
    result = agent.autonomous_analysis()
    print(f"Analysis result: {json.dumps(result, indent=2, default=str)}")
    
    # Get personalized recommendations
    recommendations = agent.personalized_recommendations("What technology stocks should I buy?")
    print(f"Recommendations: {json.dumps(recommendations, indent=2, default=str)}")
    
    # Run learning process
    learning_result = agent.learn_from_outcomes()
    print(f"Learning result: {json.dumps(learning_result, indent=2, default=str)}")
    
    print("Agentic AI system demonstration completed!")
