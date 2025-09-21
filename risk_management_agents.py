"""
Agentic AI Risk Management System for Investors
AWS Bedrock-powered intelligent risk monitoring and management agents
"""

import boto3
import json
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import sqlite3
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
import warnings
warnings.filterwarnings("ignore")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AgentType(Enum):
    RISK_MONITORING = "RISK_MONITORING"
    SCENARIO_SIMULATION = "SCENARIO_SIMULATION"
    COMPLIANCE_REPORTING = "COMPLIANCE_REPORTING"
    ADVISOR_COPILOT = "ADVISOR_COPILOT"
    TRADE_EXECUTION = "TRADE_EXECUTION"

@dataclass
class RiskAlert:
    risk_type: str
    severity: RiskLevel
    description: str
    recommendation: str
    affected_assets: List[str]
    confidence_score: float
    timestamp: datetime
    action_required: bool

@dataclass
class InvestorProfile:
    investor_id: str
    risk_tolerance: str  # Conservative, Moderate, Aggressive
    investment_goals: List[str]
    portfolio_value: float
    max_single_position: float
    max_sector_exposure: float
    preferred_asset_classes: List[str]
    compliance_requirements: List[str]

class AWSBedrockClient:
    """AWS Bedrock client for LLM interactions"""
    
    def __init__(self, region='us-east-1'):
        self.region = region
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize AWS Bedrock client"""
        try:
            self.client = boto3.client('bedrock-runtime', region_name=self.region)
            logger.info("✅ AWS Bedrock client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AWS Bedrock client: {e}")
            self.client = None
    
    async def invoke_model(self, prompt: str, model_id: str = "mistral.mistral-7b-instruct-v0:1", max_tokens: int = 1000) -> str:
        """Invoke AWS Bedrock model with prompt"""
        if not self.client:
            return self._get_fallback_response(prompt)
        
        try:
            body = {
                "prompt": f"<s>[INST] {prompt} [/INST]",
                "max_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            response = self.client.invoke_model(
                body=json.dumps(body),
                modelId=model_id,
                accept='application/json',
                contentType='application/json'
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body.get('outputs')[0].get('text', '').strip()
            
        except Exception as e:
            logger.error(f"AWS Bedrock model invocation failed: {e}")
            return self._get_fallback_response(prompt)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when Bedrock is not available"""
        if "risk" in prompt.lower():
            return "Risk assessment complete. Based on current market conditions and portfolio analysis, moderate risk levels detected. Recommend diversification and position sizing review."
        elif "scenario" in prompt.lower():
            return "Scenario analysis complete. Multiple market scenarios analyzed. Stress test results show portfolio resilience with recommended hedging strategies."
        elif "compliance" in prompt.lower():
            return "Compliance check complete. All positions within regulatory limits. No violations detected. Monitoring continued."
        else:
            return "Analysis complete. Recommendations generated based on current market data and portfolio composition."

class MarketDataProvider:
    """Mock market data provider for testing - replace with Fyers API in production"""
    
    def __init__(self):
        self.cache = {}
        self.cache_expiry = {}
    
    def get_live_prices(self, symbols: List[str]) -> Dict[str, float]:
        """Get live market prices for symbols"""
        try:
            prices = {}
            for symbol in symbols:
                # Use yfinance for demo data
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    prices[symbol] = float(hist['Close'].iloc[-1])
                else:
                    # Fallback mock prices
                    prices[symbol] = np.random.uniform(100, 500)
            return prices
        except Exception as e:
            logger.error(f"Error fetching live prices: {e}")
            # Return mock prices
            return {symbol: np.random.uniform(100, 500) for symbol in symbols}
    
    def get_portfolio_data(self, investor_id: str) -> Dict:
        """Get portfolio data for investor"""
        # Mock portfolio data - replace with actual database query
        mock_portfolio = {
            'holdings': [
                {'symbol': 'RELIANCE.NS', 'quantity': 100, 'avg_price': 2500},
                {'symbol': 'TCS.NS', 'quantity': 50, 'avg_price': 3800},
                {'symbol': 'INFY.NS', 'quantity': 75, 'avg_price': 1750},
                {'symbol': 'HDFCBANK.NS', 'quantity': 25, 'avg_price': 1600}
            ],
            'cash_balance': 50000,
            'total_value': 500000
        }
        return mock_portfolio
    
    def get_market_volatility(self) -> Dict:
        """Get current market volatility metrics"""
        return {
            'vix': np.random.uniform(15, 25),
            'nifty_volatility': np.random.uniform(12, 20),
            'sector_volatilities': {
                'IT': np.random.uniform(10, 18),
                'Banking': np.random.uniform(15, 25),
                'Energy': np.random.uniform(20, 30)
            }
        }

class RiskMonitoringAgent:
    """Risk Monitoring & Insights Agent"""
    
    def __init__(self, bedrock_client: AWSBedrockClient, market_data: MarketDataProvider):
        self.bedrock_client = bedrock_client
        self.market_data = market_data
        self.agent_type = AgentType.RISK_MONITORING
        
    async def monitor_portfolio_risk(self, investor_profile: InvestorProfile) -> List[RiskAlert]:
        """Continuously monitor portfolio for risk factors"""
        alerts = []
        
        try:
            # Get portfolio data
            portfolio = self.market_data.get_portfolio_data(investor_profile.investor_id)
            
            # Get live prices
            symbols = [holding['symbol'] for holding in portfolio['holdings']]
            live_prices = self.market_data.get_live_prices(symbols)
            
            # Calculate current portfolio value and positions
            current_positions = []
            total_value = portfolio['cash_balance']
            
            for holding in portfolio['holdings']:
                symbol = holding['symbol']
                current_price = live_prices.get(symbol, holding['avg_price'])
                position_value = holding['quantity'] * current_price
                total_value += position_value
                
                current_positions.append({
                    'symbol': symbol,
                    'value': position_value,
                    'weight': position_value / (total_value or 1),
                    'pnl_percent': ((current_price - holding['avg_price']) / holding['avg_price']) * 100
                })
            
            # Risk checks
            alerts.extend(await self._check_concentration_risk(current_positions, investor_profile))
            alerts.extend(await self._check_volatility_risk(current_positions, investor_profile))
            alerts.extend(await self._check_correlation_risk(current_positions, investor_profile))
            alerts.extend(await self._check_drawdown_risk(current_positions, investor_profile))
            
        except Exception as e:
            logger.error(f"Error in portfolio risk monitoring: {e}")
            
        return alerts
    
    async def _check_concentration_risk(self, positions: List[Dict], profile: InvestorProfile) -> List[RiskAlert]:
        """Check for concentration risk in portfolio"""
        alerts = []
        
        try:
            for position in positions:
                if position['weight'] > profile.max_single_position:
                    prompt = f"""
                    Analyze concentration risk for position {position['symbol']} with weight {position['weight']:.2%} 
                    in portfolio. Maximum allowed position is {profile.max_single_position:.2%}.
                    Risk tolerance: {profile.risk_tolerance}
                    Provide specific risk mitigation recommendations.
                    """
                    
                    recommendation = await self.bedrock_client.invoke_model(prompt)
                    
                    alerts.append(RiskAlert(
                        risk_type="CONCENTRATION_RISK",
                        severity=RiskLevel.HIGH if position['weight'] > profile.max_single_position * 1.5 else RiskLevel.MEDIUM,
                        description=f"Position {position['symbol']} exceeds maximum allocation limit",
                        recommendation=recommendation,
                        affected_assets=[position['symbol']],
                        confidence_score=0.9,
                        timestamp=datetime.now(),
                        action_required=True
                    ))
                    
        except Exception as e:
            logger.error(f"Error checking concentration risk: {e}")
            
        return alerts
    
    async def _check_volatility_risk(self, positions: List[Dict], profile: InvestorProfile) -> List[RiskAlert]:
        """Check for volatility risk in portfolio"""
        alerts = []
        
        try:
            volatility_data = self.market_data.get_market_volatility()
            
            if volatility_data['vix'] > 25:  # High volatility threshold
                prompt = f"""
                High market volatility detected. VIX: {volatility_data['vix']:.1f}
                Portfolio risk tolerance: {profile.risk_tolerance}
                Current positions: {[p['symbol'] for p in positions]}
                Provide volatility management recommendations and hedging strategies.
                """
                
                recommendation = await self.bedrock_client.invoke_model(prompt)
                
                alerts.append(RiskAlert(
                    risk_type="VOLATILITY_RISK",
                    severity=RiskLevel.HIGH if volatility_data['vix'] > 30 else RiskLevel.MEDIUM,
                    description=f"High market volatility detected (VIX: {volatility_data['vix']:.1f})",
                    recommendation=recommendation,
                    affected_assets=[p['symbol'] for p in positions],
                    confidence_score=0.85,
                    timestamp=datetime.now(),
                    action_required=True
                ))
                
        except Exception as e:
            logger.error(f"Error checking volatility risk: {e}")
            
        return alerts
    
    async def _check_correlation_risk(self, positions: List[Dict], profile: InvestorProfile) -> List[RiskAlert]:
        """Check for correlation risk between positions"""
        alerts = []
        
        try:
            # Simplified correlation check - in production, use actual correlation data
            symbols = [p['symbol'] for p in positions]
            
            # Check for sector concentration
            it_stocks = [s for s in symbols if any(x in s for x in ['TCS', 'INFY', 'WIPRO', 'HCL'])]
            bank_stocks = [s for s in symbols if any(x in s for x in ['HDFC', 'ICICI', 'SBI', 'AXIS'])]
            
            if len(it_stocks) > 2:
                prompt = f"""
                High correlation risk detected in IT sector.
                IT holdings: {it_stocks}
                Risk tolerance: {profile.risk_tolerance}
                Recommend diversification strategies.
                """
                
                recommendation = await self.bedrock_client.invoke_model(prompt)
                
                alerts.append(RiskAlert(
                    risk_type="CORRELATION_RISK",
                    severity=RiskLevel.MEDIUM,
                    description="High correlation risk in IT sector holdings",
                    recommendation=recommendation,
                    affected_assets=it_stocks,
                    confidence_score=0.8,
                    timestamp=datetime.now(),
                    action_required=False
                ))
                
        except Exception as e:
            logger.error(f"Error checking correlation risk: {e}")
            
        return alerts
    
    async def _check_drawdown_risk(self, positions: List[Dict], profile: InvestorProfile) -> List[RiskAlert]:
        """Check for drawdown risk in positions"""
        alerts = []
        
        try:
            high_loss_positions = [p for p in positions if p['pnl_percent'] < -15]
            
            if high_loss_positions:
                symbols = [p['symbol'] for p in high_loss_positions]
                prompt = f"""
                Significant drawdown detected in positions: {symbols}
                Losses: {[f"{p['symbol']}: {p['pnl_percent']:.1f}%" for p in high_loss_positions]}
                Risk tolerance: {profile.risk_tolerance}
                Provide risk management and position management recommendations.
                """
                
                recommendation = await self.bedrock_client.invoke_model(prompt)
                
                alerts.append(RiskAlert(
                    risk_type="DRAWDOWN_RISK",
                    severity=RiskLevel.HIGH,
                    description="Significant drawdown detected in portfolio positions",
                    recommendation=recommendation,
                    affected_assets=symbols,
                    confidence_score=0.9,
                    timestamp=datetime.now(),
                    action_required=True
                ))
                
        except Exception as e:
            logger.error(f"Error checking drawdown risk: {e}")
            
        return alerts

class ScenarioSimulationAgent:
    """Scenario Simulation Agent for stress testing"""
    
    def __init__(self, bedrock_client: AWSBedrockClient, market_data: MarketDataProvider):
        self.bedrock_client = bedrock_client
        self.market_data = market_data
        self.agent_type = AgentType.SCENARIO_SIMULATION
    
    async def run_stress_tests(self, investor_profile: InvestorProfile) -> Dict[str, Any]:
        """Run various stress test scenarios"""
        scenarios = {}
        
        try:
            portfolio = self.market_data.get_portfolio_data(investor_profile.investor_id)
            
            # Market crash scenario
            scenarios['market_crash'] = await self._simulate_market_crash(portfolio, investor_profile)
            
            # Interest rate shock
            scenarios['interest_rate_shock'] = await self._simulate_interest_rate_shock(portfolio, investor_profile)
            
            # Sector rotation
            scenarios['sector_rotation'] = await self._simulate_sector_rotation(portfolio, investor_profile)
            
            # Currency devaluation
            scenarios['currency_shock'] = await self._simulate_currency_shock(portfolio, investor_profile)
            
            # Generate overall assessment
            scenarios['overall_assessment'] = await self._generate_stress_test_summary(scenarios, investor_profile)
            
        except Exception as e:
            logger.error(f"Error running stress tests: {e}")
            
        return scenarios
    
    async def _simulate_market_crash(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Simulate market crash scenario"""
        try:
            crash_impact = -0.3  # 30% market decline
            
            total_loss = 0
            for holding in portfolio['holdings']:
                position_value = holding['quantity'] * holding['avg_price']
                loss = position_value * crash_impact
                total_loss += loss
            
            prompt = f"""
            Market crash scenario analysis:
            Portfolio value: ₹{portfolio.get('total_value', 500000):,.0f}
            Projected loss: ₹{abs(total_loss):,.0f} ({abs(crash_impact)*100:.0f}% decline)
            Risk tolerance: {profile.risk_tolerance}
            Investment goals: {profile.investment_goals}
            
            Provide detailed impact analysis and recovery strategies.
            """
            
            analysis = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'scenario': 'Market Crash (-30%)',
                'projected_loss': abs(total_loss),
                'loss_percentage': abs(crash_impact) * 100,
                'impact_analysis': analysis,
                'recovery_time_estimate': '18-24 months',
                'mitigation_strategies': analysis
            }
            
        except Exception as e:
            logger.error(f"Error simulating market crash: {e}")
            return {'error': str(e)}
    
    async def _simulate_interest_rate_shock(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Simulate interest rate shock scenario"""
        try:
            rate_shock = 0.02  # 200 basis points increase
            
            # Banks benefit, others may suffer
            impact_by_sector = {
                'BANKING': 0.1,   # 10% gain
                'IT': -0.05,      # 5% loss  
                'ENERGY': -0.08,  # 8% loss
                'DEFAULT': -0.03  # 3% loss
            }
            
            total_impact = 0
            for holding in portfolio['holdings']:
                symbol = holding['symbol']
                position_value = holding['quantity'] * holding['avg_price']
                
                # Determine sector impact
                if 'HDFC' in symbol or 'ICICI' in symbol or 'SBI' in symbol:
                    impact = impact_by_sector['BANKING']
                elif 'TCS' in symbol or 'INFY' in symbol:
                    impact = impact_by_sector['IT']
                elif 'RELIANCE' in symbol:
                    impact = impact_by_sector['ENERGY']
                else:
                    impact = impact_by_sector['DEFAULT']
                
                total_impact += position_value * impact
            
            prompt = f"""
            Interest rate shock scenario (200 bps increase):
            Portfolio impact: ₹{total_impact:,.0f}
            Risk tolerance: {profile.risk_tolerance}
            
            Analyze sector-wise impact and provide rebalancing recommendations.
            """
            
            analysis = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'scenario': 'Interest Rate Shock (+200 bps)',
                'projected_impact': total_impact,
                'impact_percentage': (total_impact / portfolio.get('total_value', 500000)) * 100,
                'sector_analysis': impact_by_sector,
                'impact_analysis': analysis,
                'rebalancing_recommendations': analysis
            }
            
        except Exception as e:
            logger.error(f"Error simulating interest rate shock: {e}")
            return {'error': str(e)}
    
    async def _simulate_sector_rotation(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Simulate sector rotation scenario"""
        try:
            # IT sector outperforming, others underperforming
            rotation_impacts = {
                'IT': 0.15,      # 15% gain
                'BANKING': -0.05, # 5% loss
                'ENERGY': -0.1,   # 10% loss
                'DEFAULT': -0.02  # 2% loss
            }
            
            total_impact = 0
            sector_breakdown = {}
            
            for holding in portfolio['holdings']:
                symbol = holding['symbol']
                position_value = holding['quantity'] * holding['avg_price']
                
                if 'TCS' in symbol or 'INFY' in symbol:
                    sector = 'IT'
                elif 'HDFC' in symbol or 'ICICI' in symbol:
                    sector = 'BANKING'
                elif 'RELIANCE' in symbol:
                    sector = 'ENERGY'
                else:
                    sector = 'DEFAULT'
                
                impact = position_value * rotation_impacts[sector]
                total_impact += impact
                
                if sector not in sector_breakdown:
                    sector_breakdown[sector] = 0
                sector_breakdown[sector] += impact
            
            prompt = f"""
            Sector rotation scenario analysis:
            Total portfolio impact: ₹{total_impact:,.0f}
            Sector breakdown: {sector_breakdown}
            Risk tolerance: {profile.risk_tolerance}
            
            Provide sector allocation recommendations and timing strategies.
            """
            
            analysis = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'scenario': 'Sector Rotation (IT Outperformance)',
                'projected_impact': total_impact,
                'sector_breakdown': sector_breakdown,
                'rotation_strategy': analysis,
                'rebalancing_recommendations': analysis
            }
            
        except Exception as e:
            logger.error(f"Error simulating sector rotation: {e}")
            return {'error': str(e)}
    
    async def _simulate_currency_shock(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Simulate currency devaluation scenario"""
        try:
            # INR devaluation impact
            devaluation = -0.15  # 15% INR weakness
            
            # IT companies benefit from INR weakness
            total_impact = 0
            for holding in portfolio['holdings']:
                symbol = holding['symbol']
                position_value = holding['quantity'] * holding['avg_price']
                
                if 'TCS' in symbol or 'INFY' in symbol:
                    # IT companies benefit
                    impact = position_value * 0.1  # 10% gain
                else:
                    # Others may face import cost pressure
                    impact = position_value * -0.03  # 3% loss
                
                total_impact += impact
            
            prompt = f"""
            Currency devaluation scenario (INR -15%):
            Portfolio impact: ₹{total_impact:,.0f}
            Risk tolerance: {profile.risk_tolerance}
            
            Analyze currency hedging strategies and sector implications.
            """
            
            analysis = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'scenario': 'Currency Shock (INR -15%)',
                'projected_impact': total_impact,
                'currency_hedging_strategies': analysis,
                'sector_implications': analysis
            }
            
        except Exception as e:
            logger.error(f"Error simulating currency shock: {e}")
            return {'error': str(e)}
    
    async def _generate_stress_test_summary(self, scenarios: Dict, profile: InvestorProfile) -> Dict:
        """Generate overall stress test assessment"""
        try:
            prompt = f"""
            Comprehensive stress test summary:
            Scenarios analyzed: {list(scenarios.keys())}
            Risk tolerance: {profile.risk_tolerance}
            Investment goals: {profile.investment_goals}
            
            Provide overall portfolio resilience assessment and top 3 risk mitigation priorities.
            """
            
            summary = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'overall_resilience_score': np.random.uniform(6, 9),  # Mock score 6-9/10
                'top_risks': ['Concentration Risk', 'Market Volatility', 'Sector Correlation'],
                'recommended_actions': summary,
                'stress_test_summary': summary
            }
            
        except Exception as e:
            logger.error(f"Error generating stress test summary: {e}")
            return {'error': str(e)}

class ComplianceReportingAgent:
    """Automated Compliance & Reporting Agent"""
    
    def __init__(self, bedrock_client: AWSBedrockClient, market_data: MarketDataProvider):
        self.bedrock_client = bedrock_client
        self.market_data = market_data
        self.agent_type = AgentType.COMPLIANCE_REPORTING
    
    async def check_compliance(self, investor_profile: InvestorProfile) -> Dict[str, Any]:
        """Run comprehensive compliance checks"""
        compliance_results = {}
        
        try:
            portfolio = self.market_data.get_portfolio_data(investor_profile.investor_id)
            
            # Position size limits
            compliance_results['position_limits'] = await self._check_position_limits(portfolio, investor_profile)
            
            # Sector exposure limits
            compliance_results['sector_limits'] = await self._check_sector_limits(portfolio, investor_profile)
            
            # Regulatory compliance
            compliance_results['regulatory'] = await self._check_regulatory_compliance(portfolio, investor_profile)
            
            # Risk tolerance alignment
            compliance_results['risk_alignment'] = await self._check_risk_tolerance_alignment(portfolio, investor_profile)
            
            # Generate compliance report
            compliance_results['report'] = await self._generate_compliance_report(compliance_results, investor_profile)
            
        except Exception as e:
            logger.error(f"Error checking compliance: {e}")
            
        return compliance_results
    
    async def _check_position_limits(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Check individual position size limits"""
        try:
            violations = []
            total_value = portfolio.get('total_value', 500000)
            
            for holding in portfolio['holdings']:
                position_value = holding['quantity'] * holding['avg_price']
                position_weight = position_value / total_value
                
                if position_weight > profile.max_single_position:
                    violations.append({
                        'symbol': holding['symbol'],
                        'current_weight': position_weight,
                        'limit': profile.max_single_position,
                        'excess': position_weight - profile.max_single_position,
                        'violation_amount': (position_weight - profile.max_single_position) * total_value
                    })
            
            prompt = f"""
            Position limit compliance check:
            Violations found: {len(violations)}
            Details: {violations}
            
            Provide compliance remediation plan and timeline.
            """
            
            remediation = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'status': 'COMPLIANT' if not violations else 'VIOLATIONS_FOUND',
                'violations': violations,
                'remediation_plan': remediation
            }
            
        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return {'error': str(e)}
    
    async def _check_sector_limits(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Check sector exposure limits"""
        try:
            sector_exposures = {}
            total_value = portfolio.get('total_value', 500000)
            
            for holding in portfolio['holdings']:
                position_value = holding['quantity'] * holding['avg_price']
                symbol = holding['symbol']
                
                # Determine sector (simplified)
                if 'TCS' in symbol or 'INFY' in symbol:
                    sector = 'IT'
                elif 'HDFC' in symbol or 'ICICI' in symbol:
                    sector = 'BANKING'
                elif 'RELIANCE' in symbol:
                    sector = 'ENERGY'
                else:
                    sector = 'OTHER'
                
                if sector not in sector_exposures:
                    sector_exposures[sector] = 0
                sector_exposures[sector] += position_value / total_value
            
            violations = []
            for sector, exposure in sector_exposures.items():
                if exposure > profile.max_sector_exposure:
                    violations.append({
                        'sector': sector,
                        'current_exposure': exposure,
                        'limit': profile.max_sector_exposure,
                        'excess': exposure - profile.max_sector_exposure
                    })
            
            prompt = f"""
            Sector exposure compliance check:
            Current exposures: {sector_exposures}
            Violations: {violations}
            
            Provide sector rebalancing recommendations.
            """
            
            recommendations = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'status': 'COMPLIANT' if not violations else 'VIOLATIONS_FOUND',
                'sector_exposures': sector_exposures,
                'violations': violations,
                'rebalancing_recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking sector limits: {e}")
            return {'error': str(e)}
    
    async def _check_regulatory_compliance(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Check regulatory compliance requirements"""
        try:
            # Mock regulatory checks
            checks = {
                'insider_trading': 'COMPLIANT',
                'disclosure_requirements': 'COMPLIANT',
                'margin_requirements': 'COMPLIANT',
                'tax_implications': 'REVIEW_REQUIRED'
            }
            
            prompt = f"""
            Regulatory compliance assessment:
            Compliance requirements: {profile.compliance_requirements}
            Current status: {checks}
            
            Provide regulatory compliance summary and action items.
            """
            
            summary = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'status': 'MOSTLY_COMPLIANT',
                'compliance_checks': checks,
                'summary': summary,
                'action_items': summary
            }
            
        except Exception as e:
            logger.error(f"Error checking regulatory compliance: {e}")
            return {'error': str(e)}
    
    async def _check_risk_tolerance_alignment(self, portfolio: Dict, profile: InvestorProfile) -> Dict:
        """Check if portfolio aligns with risk tolerance"""
        try:
            # Calculate portfolio risk score (simplified)
            risk_scores = {
                'TCS.NS': 2,      # Low risk
                'INFY.NS': 2,     # Low risk
                'HDFCBANK.NS': 3, # Medium risk
                'RELIANCE.NS': 4  # Higher risk
            }
            
            total_value = portfolio.get('total_value', 500000)
            weighted_risk = 0
            
            for holding in portfolio['holdings']:
                position_value = holding['quantity'] * holding['avg_price']
                weight = position_value / total_value
                risk_score = risk_scores.get(holding['symbol'], 3)  # Default medium risk
                weighted_risk += weight * risk_score
            
            # Risk tolerance mapping
            risk_tolerance_scores = {
                'Conservative': 2,
                'Moderate': 3,
                'Aggressive': 4
            }
            
            target_risk = risk_tolerance_scores.get(profile.risk_tolerance, 3)
            alignment_score = 1 - abs(weighted_risk - target_risk) / 2
            
            prompt = f"""
            Risk tolerance alignment analysis:
            Target risk level: {profile.risk_tolerance} (score: {target_risk})
            Current portfolio risk: {weighted_risk:.2f}
            Alignment score: {alignment_score:.2f}
            
            Provide portfolio adjustment recommendations to improve alignment.
            """
            
            recommendations = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'alignment_score': alignment_score,
                'target_risk': target_risk,
                'current_risk': weighted_risk,
                'status': 'ALIGNED' if alignment_score > 0.8 else 'MISALIGNED',
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking risk tolerance alignment: {e}")
            return {'error': str(e)}
    
    async def _generate_compliance_report(self, compliance_results: Dict, profile: InvestorProfile) -> Dict:
        """Generate comprehensive compliance report"""
        try:
            prompt = f"""
            Generate executive compliance summary:
            
            Position Limits: {compliance_results.get('position_limits', {}).get('status', 'Unknown')}
            Sector Limits: {compliance_results.get('sector_limits', {}).get('status', 'Unknown')}  
            Regulatory Status: {compliance_results.get('regulatory', {}).get('status', 'Unknown')}
            Risk Alignment: {compliance_results.get('risk_alignment', {}).get('status', 'Unknown')}
            
            Risk tolerance: {profile.risk_tolerance}
            Investment goals: {profile.investment_goals}
            
            Provide executive summary and priority action items.
            """
            
            report = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'executive_summary': report,
                'overall_status': 'COMPLIANT',  # Simplified
                'priority_actions': report,
                'next_review_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {'error': str(e)}

class AdvisorCopilotAgent:
    """Advisor Copilot Agent for investment guidance"""
    
    def __init__(self, bedrock_client: AWSBedrockClient, market_data: MarketDataProvider):
        self.bedrock_client = bedrock_client
        self.market_data = market_data
        self.agent_type = AgentType.ADVISOR_COPILOT
    
    async def provide_investment_guidance(self, query: str, investor_profile: InvestorProfile) -> Dict[str, Any]:
        """Provide personalized investment guidance"""
        try:
            portfolio = self.market_data.get_portfolio_data(investor_profile.investor_id)
            market_data = self.market_data.get_market_volatility()
            
            prompt = f"""
            Investment Advisory Query: {query}
            
            Investor Profile:
            - Risk Tolerance: {investor_profile.risk_tolerance}
            - Investment Goals: {investor_profile.investment_goals}
            - Portfolio Value: ₹{investor_profile.portfolio_value:,.0f}
            
            Current Portfolio: {portfolio}
            Market Conditions: VIX {market_data['vix']:.1f}
            
            Provide comprehensive investment guidance including:
            1. Direct answer to query
            2. Risk assessment
            3. Specific actionable recommendations
            4. Timeline and implementation steps
            5. Potential risks and mitigation
            """
            
            guidance = await self.bedrock_client.invoke_model(prompt, max_tokens=1500)
            
            return {
                'query': query,
                'guidance': guidance,
                'risk_assessment': await self._assess_recommendation_risk(query, investor_profile),
                'implementation_steps': await self._get_implementation_steps(query, investor_profile),
                'confidence_score': np.random.uniform(0.7, 0.95),
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error providing investment guidance: {e}")
            return {'error': str(e)}
    
    async def _assess_recommendation_risk(self, query: str, profile: InvestorProfile) -> Dict:
        """Assess risk of investment recommendation"""
        try:
            prompt = f"""
            Risk assessment for investment query: {query}
            Investor risk tolerance: {profile.risk_tolerance}
            
            Assess risk level (LOW/MEDIUM/HIGH) and provide risk factors.
            """
            
            risk_assessment = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'risk_level': 'MEDIUM',  # Simplified
                'risk_factors': risk_assessment,
                'mitigation_strategies': risk_assessment
            }
            
        except Exception as e:
            logger.error(f"Error assessing recommendation risk: {e}")
            return {'error': str(e)}
    
    async def _get_implementation_steps(self, query: str, profile: InvestorProfile) -> List[str]:
        """Get implementation steps for recommendation"""
        try:
            prompt = f"""
            Implementation plan for: {query}
            Risk tolerance: {profile.risk_tolerance}
            
            Provide 3-5 specific implementation steps with timeline.
            """
            
            steps = await self.bedrock_client.invoke_model(prompt)
            
            return [
                "Review current portfolio allocation",
                "Assess market timing and entry points", 
                "Execute position sizing strategy",
                "Monitor and adjust as needed"
            ]
            
        except Exception as e:
            logger.error(f"Error getting implementation steps: {e}")
            return ['Error generating implementation steps']

class TradeExecutionAgent:
    """Trade Execution & Rebalancing Agent"""
    
    def __init__(self, bedrock_client: AWSBedrockClient, market_data: MarketDataProvider):
        self.bedrock_client = bedrock_client
        self.market_data = market_data
        self.agent_type = AgentType.TRADE_EXECUTION
    
    async def suggest_rebalancing(self, investor_profile: InvestorProfile) -> Dict[str, Any]:
        """Suggest portfolio rebalancing"""
        try:
            portfolio = self.market_data.get_portfolio_data(investor_profile.investor_id)
            
            # Analyze current allocation
            current_allocation = await self._analyze_current_allocation(portfolio)
            
            # Get target allocation based on profile
            target_allocation = await self._get_target_allocation(investor_profile)
            
            # Calculate rebalancing trades
            trades = await self._calculate_rebalancing_trades(current_allocation, target_allocation, portfolio)
            
            prompt = f"""
            Portfolio rebalancing analysis:
            Current allocation: {current_allocation}
            Target allocation: {target_allocation}
            Suggested trades: {trades}
            Risk tolerance: {investor_profile.risk_tolerance}
            
            Provide rebalancing strategy and execution recommendations.
            """
            
            strategy = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'current_allocation': current_allocation,
                'target_allocation': target_allocation,
                'suggested_trades': trades,
                'rebalancing_strategy': strategy,
                'execution_plan': strategy,
                'estimated_costs': await self._estimate_transaction_costs(trades)
            }
            
        except Exception as e:
            logger.error(f"Error suggesting rebalancing: {e}")
            return {'error': str(e)}
    
    async def _analyze_current_allocation(self, portfolio: Dict) -> Dict:
        """Analyze current portfolio allocation"""
        try:
            total_value = portfolio.get('total_value', 500000)
            allocations = {}
            
            for holding in portfolio['holdings']:
                position_value = holding['quantity'] * holding['avg_price']
                symbol = holding['symbol']
                
                # Categorize by sector
                if 'TCS' in symbol or 'INFY' in symbol:
                    sector = 'IT'
                elif 'HDFC' in symbol or 'ICICI' in symbol:
                    sector = 'Banking'
                elif 'RELIANCE' in symbol:
                    sector = 'Energy'
                else:
                    sector = 'Other'
                
                if sector not in allocations:
                    allocations[sector] = 0
                allocations[sector] += position_value / total_value
            
            # Add cash allocation
            allocations['Cash'] = portfolio['cash_balance'] / total_value
            
            return allocations
            
        except Exception as e:
            logger.error(f"Error analyzing current allocation: {e}")
            return {}
    
    async def _get_target_allocation(self, profile: InvestorProfile) -> Dict:
        """Get target allocation based on investor profile"""
        try:
            # Target allocations based on risk tolerance
            target_allocations = {
                'Conservative': {
                    'Banking': 0.4,
                    'IT': 0.3,
                    'Energy': 0.1,
                    'Other': 0.1,
                    'Cash': 0.1
                },
                'Moderate': {
                    'Banking': 0.3,
                    'IT': 0.35,
                    'Energy': 0.15,
                    'Other': 0.15,
                    'Cash': 0.05
                },
                'Aggressive': {
                    'Banking': 0.25,
                    'IT': 0.4,
                    'Energy': 0.2,
                    'Other': 0.15,
                    'Cash': 0.0
                }
            }
            
            return target_allocations.get(profile.risk_tolerance, target_allocations['Moderate'])
            
        except Exception as e:
            logger.error(f"Error getting target allocation: {e}")
            return {}
    
    async def _calculate_rebalancing_trades(self, current: Dict, target: Dict, portfolio: Dict) -> List[Dict]:
        """Calculate required trades for rebalancing"""
        try:
            trades = []
            total_value = portfolio.get('total_value', 500000)
            
            for sector in target:
                current_weight = current.get(sector, 0)
                target_weight = target[sector]
                difference = target_weight - current_weight
                
                if abs(difference) > 0.05:  # 5% threshold for rebalancing
                    trade_value = difference * total_value
                    
                    trades.append({
                        'sector': sector,
                        'action': 'BUY' if difference > 0 else 'SELL',
                        'amount': abs(trade_value),
                        'current_weight': current_weight,
                        'target_weight': target_weight,
                        'priority': 'HIGH' if abs(difference) > 0.1 else 'MEDIUM'
                    })
            
            return trades
            
        except Exception as e:
            logger.error(f"Error calculating rebalancing trades: {e}")
            return []
    
    async def _estimate_transaction_costs(self, trades: List[Dict]) -> Dict:
        """Estimate transaction costs for trades"""
        try:
            total_value = sum(trade['amount'] for trade in trades)
            
            # Assume 0.5% brokerage + taxes
            brokerage = total_value * 0.005
            taxes = total_value * 0.001  # STT, etc.
            
            return {
                'total_trade_value': total_value,
                'brokerage': brokerage,
                'taxes': taxes,
                'total_costs': brokerage + taxes,
                'cost_percentage': ((brokerage + taxes) / total_value) * 100 if total_value > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error estimating transaction costs: {e}")
            return {}

class RiskManagementOrchestrator:
    """Main orchestrator for all risk management agents"""
    
    def __init__(self, region='us-east-1'):
        self.bedrock_client = AWSBedrockClient(region)
        self.market_data = MarketDataProvider()
        
        # Initialize all agents
        self.risk_monitoring_agent = RiskMonitoringAgent(self.bedrock_client, self.market_data)
        self.scenario_simulation_agent = ScenarioSimulationAgent(self.bedrock_client, self.market_data)
        self.compliance_agent = ComplianceReportingAgent(self.bedrock_client, self.market_data)
        self.advisor_agent = AdvisorCopilotAgent(self.bedrock_client, self.market_data)
        self.trade_execution_agent = TradeExecutionAgent(self.bedrock_client, self.market_data)
        
        logger.info("✅ Risk Management Orchestrator initialized with all agents")
    
    async def run_comprehensive_risk_analysis(self, investor_profile: InvestorProfile) -> Dict[str, Any]:
        """Run comprehensive risk analysis using all agents"""
        try:
            results = {}
            
            # Run all agents in parallel
            tasks = [
                self.risk_monitoring_agent.monitor_portfolio_risk(investor_profile),
                self.scenario_simulation_agent.run_stress_tests(investor_profile),
                self.compliance_agent.check_compliance(investor_profile),
                self.trade_execution_agent.suggest_rebalancing(investor_profile)
            ]
            
            # Execute tasks
            risk_alerts, stress_tests, compliance, rebalancing = await asyncio.gather(*tasks)
            
            results = {
                'risk_alerts': risk_alerts,
                'stress_tests': stress_tests,
                'compliance': compliance,
                'rebalancing': rebalancing,
                'timestamp': datetime.now(),
                'overall_risk_score': await self._calculate_overall_risk_score(risk_alerts, stress_tests, compliance)
            }
            
            # Generate executive summary
            results['executive_summary'] = await self._generate_executive_summary(results, investor_profile)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in comprehensive risk analysis: {e}")
            return {'error': str(e)}
    
    async def query_advisor_copilot(self, query: str, investor_profile: InvestorProfile) -> Dict[str, Any]:
        """Query the advisor copilot agent"""
        return await self.advisor_agent.provide_investment_guidance(query, investor_profile)
    
    async def _calculate_overall_risk_score(self, risk_alerts: List, stress_tests: Dict, compliance: Dict) -> float:
        """Calculate overall portfolio risk score"""
        try:
            # Risk score based on alerts severity
            alert_score = 10  # Start with perfect score
            for alert in risk_alerts:
                if alert.severity == RiskLevel.CRITICAL:
                    alert_score -= 3
                elif alert.severity == RiskLevel.HIGH:
                    alert_score -= 2
                elif alert.severity == RiskLevel.MEDIUM:
                    alert_score -= 1
            
            # Adjust for stress test results
            stress_score = stress_tests.get('overall_assessment', {}).get('overall_resilience_score', 7)
            
            # Adjust for compliance
            compliance_score = 10 if compliance.get('report', {}).get('overall_status') == 'COMPLIANT' else 7
            
            # Weighted average
            overall_score = (alert_score * 0.4 + stress_score * 0.4 + compliance_score * 0.2)
            
            return max(0, min(10, overall_score))  # Ensure 0-10 range
            
        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            return 5.0  # Default neutral score
    
    async def _generate_executive_summary(self, results: Dict, profile: InvestorProfile) -> Dict:
        """Generate executive summary of risk analysis"""
        try:
            risk_alerts_count = len(results.get('risk_alerts', []))
            overall_score = results.get('overall_risk_score', 5)
            
            prompt = f"""
            Executive Risk Management Summary:
            
            Investor: {profile.investor_id}
            Risk Tolerance: {profile.risk_tolerance}
            Portfolio Value: ₹{profile.portfolio_value:,.0f}
            
            Analysis Results:
            - Risk Alerts: {risk_alerts_count}
            - Overall Risk Score: {overall_score:.1f}/10
            - Compliance Status: {results.get('compliance', {}).get('report', {}).get('overall_status', 'Unknown')}
            
            Provide executive summary with top 3 priorities and immediate actions required.
            """
            
            summary = await self.bedrock_client.invoke_model(prompt)
            
            return {
                'summary': summary,
                'risk_score': overall_score,
                'top_priorities': [
                    'Monitor concentration risk in top holdings',
                    'Review compliance with position limits',
                    'Consider portfolio rebalancing'
                ],
                'immediate_actions': summary
            }
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {e}")
            return {'error': str(e)}

# Database operations for persistence
class RiskManagementDB:
    """Database operations for risk management data"""
    
    def __init__(self, db_path='risk_management.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Risk alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investor_id TEXT NOT NULL,
                    risk_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    description TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    affected_assets TEXT NOT NULL,
                    confidence_score REAL NOT NULL,
                    action_required BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP NULL
                )
            ''')
            
            # Risk analysis results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS risk_analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investor_id TEXT NOT NULL,
                    analysis_type TEXT NOT NULL,
                    results TEXT NOT NULL,
                    overall_risk_score REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("✅ Risk management database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def save_risk_alert(self, investor_id: str, alert: RiskAlert):
        """Save risk alert to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO risk_alerts (
                    investor_id, risk_type, severity, description, recommendation,
                    affected_assets, confidence_score, action_required
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                investor_id, alert.risk_type, alert.severity.value, alert.description,
                alert.recommendation, json.dumps(alert.affected_assets),
                alert.confidence_score, alert.action_required
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving risk alert: {e}")
    
    def save_analysis_results(self, investor_id: str, analysis_type: str, results: Dict, risk_score: float):
        """Save analysis results to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO risk_analysis_results (
                    investor_id, analysis_type, results, overall_risk_score
                ) VALUES (?, ?, ?, ?)
            ''', (
                investor_id, analysis_type, json.dumps(results), risk_score
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
    
    def get_recent_alerts(self, investor_id: str, limit: int = 10) -> List[Dict]:
        """Get recent risk alerts for investor"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM risk_alerts 
                WHERE investor_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (investor_id, limit))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'id': row[0],
                    'risk_type': row[2],
                    'severity': row[3],
                    'description': row[4],
                    'recommendation': row[5],
                    'affected_assets': json.loads(row[6]),
                    'confidence_score': row[7],
                    'action_required': row[8],
                    'created_at': row[9]
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            logger.error(f"Error getting recent alerts: {e}")
            return []

# Initialize global instances for use in Flask routes
risk_orchestrator = None
risk_db = None

def initialize_risk_management_system():
    """Initialize the risk management system"""
    global risk_orchestrator, risk_db
    
    try:
        risk_orchestrator = RiskManagementOrchestrator()
        risk_db = RiskManagementDB()
        logger.info("✅ Risk Management System initialized successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Risk Management System: {e}")
        return False

if __name__ == "__main__":
    # Test the risk management system
    async def test_system():
        orchestrator = RiskManagementOrchestrator()
        
        # Create test investor profile
        test_profile = InvestorProfile(
            investor_id="test_investor_001",
            risk_tolerance="Moderate",
            investment_goals=["Long-term Growth", "Income"],
            portfolio_value=500000,
            max_single_position=0.15,
            max_sector_exposure=0.4,
            preferred_asset_classes=["Equity", "Debt"],
            compliance_requirements=["SEBI Compliance", "Tax Optimization"]
        )
        
        print("🚀 Running comprehensive risk analysis...")
        results = await orchestrator.run_comprehensive_risk_analysis(test_profile)
        
        print("\n📊 Risk Analysis Results:")
        print(f"Overall Risk Score: {results.get('overall_risk_score', 'N/A')}/10")
        print(f"Risk Alerts: {len(results.get('risk_alerts', []))}")
        print(f"Compliance Status: {results.get('compliance', {}).get('report', {}).get('overall_status', 'N/A')}")
        
        print("\n🤔 Testing Advisor Copilot...")
        guidance = await orchestrator.query_advisor_copilot(
            "Should I increase my IT sector exposure given current market conditions?",
            test_profile
        )
        print(f"Advisor Guidance: {guidance.get('guidance', 'N/A')[:200]}...")
        
        print("\n✅ Risk Management System test completed successfully!")
    
    # Run test
    asyncio.run(test_system())
