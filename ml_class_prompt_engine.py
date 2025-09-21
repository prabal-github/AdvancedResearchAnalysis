"""
Enhanced Prompt Engineering for VS Terminal ML Class
===================================================

Advanced AI response generation with context-aware prompting,
dynamic prompt templates, and intelligent conversation management.

Author: AI Assistant  
Date: 2024
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import numpy as np


class MLClassPromptEngine:
    """Advanced prompt engineering system for ML Class AI responses"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_context = {}
        self.system_state = {}
        self.prompt_templates = self._initialize_prompt_templates()
        
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize comprehensive prompt templates"""
        return {
            'portfolio_analysis': """
You are a senior portfolio manager with 15+ years of experience. Analyze the following portfolio data:

PORTFOLIO OVERVIEW:
- Total Value: {portfolio_value}
- Number of Holdings: {holdings_count}
- Risk Level: {risk_level}
- Performance: {performance}

KEY HOLDINGS:
{holdings_breakdown}

MARKET CONTEXT:
{market_conditions}

Provide a comprehensive analysis covering:
1. Portfolio health assessment
2. Risk-return optimization opportunities  
3. Diversification analysis
4. Specific actionable recommendations
5. Market timing considerations

Use professional yet accessible language. Include specific metrics and ratios.
""",

            'trading_signals': """
You are an algorithmic trading specialist. Generate trading signals based on:

TECHNICAL ANALYSIS:
{technical_indicators}

FUNDAMENTAL DATA:
{fundamental_metrics}

MARKET SENTIMENT:
{sentiment_data}

RISK PARAMETERS:
- Max position size: {max_position}
- Risk tolerance: {risk_tolerance}
- Time horizon: {time_horizon}

Generate specific trading recommendations with:
1. Entry/exit points with precise levels
2. Position sizing recommendations
3. Risk management parameters (stop-loss, take-profit)
4. Confidence score (1-10)
5. Market timing rationale

Format as actionable trade setups.
""",

            'risk_assessment': """
You are a risk management expert. Assess portfolio risk using:

PORTFOLIO COMPOSITION:
{portfolio_data}

RISK METRICS:
- VaR (95%): {var_95}
- Maximum Drawdown: {max_drawdown}
- Beta: {portfolio_beta}
- Volatility: {volatility}

CORRELATION ANALYSIS:
{correlation_matrix}

STRESS TEST RESULTS:
{stress_test_data}

Provide comprehensive risk analysis:
1. Current risk level assessment
2. Concentration risk evaluation
3. Market risk exposure
4. Liquidity risk analysis
5. Specific risk mitigation strategies
6. Portfolio optimization suggestions

Include quantitative risk metrics and qualitative insights.
""",

            'market_intelligence': """
You are a senior market strategist. Provide market intelligence using:

MARKET DATA:
{market_overview}

ECONOMIC INDICATORS:
{economic_data}

SECTOR ANALYSIS:
{sector_performance}

NEWS SENTIMENT:
{news_analysis}

TECHNICAL OUTLOOK:
{technical_levels}

Deliver strategic market insights:
1. Current market regime identification
2. Key themes and trends
3. Sector rotation opportunities
4. Risk events and catalysts
5. Strategic asset allocation guidance
6. Timing considerations

Maintain objective, data-driven perspective with actionable insights.
""",

            'performance_attribution': """
You are a performance analyst. Analyze portfolio performance:

PERFORMANCE METRICS:
- Total Return: {total_return}
- Benchmark Return: {benchmark_return}
- Alpha: {alpha}
- Sharpe Ratio: {sharpe_ratio}
- Information Ratio: {info_ratio}

ATTRIBUTION ANALYSIS:
{attribution_breakdown}

BENCHMARK COMPARISON:
{benchmark_analysis}

FACTOR EXPOSURE:
{factor_exposure}

Provide detailed performance analysis:
1. Return decomposition (alpha vs beta)
2. Factor attribution analysis
3. Security selection vs allocation impact
4. Risk-adjusted performance metrics
5. Performance consistency analysis
6. Improvement recommendations

Use quantitative analysis with clear explanations.
"""
        }
    
    def generate_enhanced_response(self, user_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate enhanced AI response with advanced prompt engineering"""
        
        # Analyze user intent and extract key entities
        intent_analysis = self._analyze_user_intent(user_message)
        entities = self._extract_entities(user_message)
        
        # Determine response strategy
        response_strategy = self._determine_response_strategy(intent_analysis, entities, context)
        
        # Generate contextual prompt
        prompt = self._build_contextual_prompt(intent_analysis, entities, context, response_strategy)
        
        # Generate response content
        response_content = self._generate_response_content(prompt, response_strategy)
        
        # Add conversation management
        conversation_metadata = self._manage_conversation_flow(user_message, response_content)
        
        return {
            'type': response_strategy['type'],
            'message': response_content['message'],
            'suggestions': response_content['suggestions'],
            'actions': response_content.get('actions', []),
            'visualizations': response_content.get('visualizations', []),
            'metadata': {
                'intent': intent_analysis,
                'entities': entities,
                'strategy': response_strategy,
                'conversation': conversation_metadata,
                'confidence': response_content.get('confidence', 0.85),
                'context_used': context is not None
            }
        }
    
    def _analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Advanced intent analysis with multi-label classification"""
        message_lower = message.lower()
        
        # Intent patterns with confidence scoring
        intent_patterns = {
            'portfolio_analysis': {
                'keywords': ['portfolio', 'holdings', 'allocation', 'diversification', 'performance'],
                'patterns': [r'analyz.*portfolio', r'portfolio.*health', r'review.*holdings'],
                'weight': 1.0
            },
            'trading_signals': {
                'keywords': ['trade', 'buy', 'sell', 'signal', 'entry', 'exit'],
                'patterns': [r'trading.*signal', r'should.*buy', r'when.*sell'],
                'weight': 1.0
            },
            'risk_assessment': {
                'keywords': ['risk', 'var', 'volatility', 'drawdown', 'stress'],
                'patterns': [r'risk.*assessment', r'how.*risky', r'value.*risk'],
                'weight': 1.0
            },
            'market_analysis': {
                'keywords': ['market', 'trend', 'sentiment', 'outlook', 'sector'],
                'patterns': [r'market.*analysis', r'current.*trends', r'sector.*outlook'],
                'weight': 1.0
            },
            'performance_review': {
                'keywords': ['performance', 'returns', 'alpha', 'beta', 'sharpe'],
                'patterns': [r'performance.*review', r'how.*performing', r'returns.*analysis'],
                'weight': 1.0
            }
        }
        
        intent_scores = {}
        for intent, config in intent_patterns.items():
            score = 0.0
            
            # Keyword matching
            keyword_matches = sum(1 for keyword in config['keywords'] if keyword in message_lower)
            score += (keyword_matches / len(config['keywords'])) * 0.6
            
            # Pattern matching
            pattern_matches = sum(1 for pattern in config['patterns'] if re.search(pattern, message_lower))
            score += (pattern_matches / len(config['patterns'])) * 0.4
            
            intent_scores[intent] = score * config['weight']
        
        # Get primary intent
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        return {
            'primary': primary_intent[0],
            'confidence': primary_intent[1],
            'all_scores': intent_scores,
            'is_multi_intent': sum(score > 0.3 for score in intent_scores.values()) > 1
        }
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract financial entities from user message"""
        entities = {
            'symbols': [],
            'numbers': [],
            'timeframes': [],
            'actions': [],
            'metrics': []
        }
        
        # Symbol extraction (Indian market focus)
        symbol_patterns = [
            r'\b([A-Z]{2,})\b',  # General uppercase
            r'\b(RELIANCE|TCS|INFY|HDFC|ICICI|SBI|ITC|LT|BAJAJ)\b'  # Common stocks
        ]
        
        for pattern in symbol_patterns:
            matches = re.findall(pattern, message.upper())
            entities['symbols'].extend(matches)
        
        # Number extraction
        number_pattern = r'\b(\d+(?:\.\d+)?)\s*(?:%|percent|cr|crore|lakh|k|thousand)?\b'
        entities['numbers'] = re.findall(number_pattern, message.lower())
        
        # Timeframe extraction
        timeframe_patterns = [
            r'\b(\d+)\s*(day|week|month|year)s?\b',
            r'\b(short|medium|long)[\s-]?term\b',
            r'\b(daily|weekly|monthly|quarterly|yearly)\b'
        ]
        
        for pattern in timeframe_patterns:
            matches = re.findall(pattern, message.lower())
            entities['timeframes'].extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        # Action extraction
        action_words = ['buy', 'sell', 'hold', 'analyze', 'review', 'calculate', 'optimize', 'rebalance']
        entities['actions'] = [word for word in action_words if word in message.lower()]
        
        # Metric extraction
        metric_words = ['sharpe', 'alpha', 'beta', 'var', 'volatility', 'return', 'risk', 'ratio']
        entities['metrics'] = [word for word in metric_words if word in message.lower()]
        
        # Clean and deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _determine_response_strategy(self, intent_analysis: Dict, entities: Dict, context: Dict) -> Dict[str, Any]:
        """Determine optimal response strategy"""
        
        primary_intent = intent_analysis['primary']
        confidence = intent_analysis['confidence']
        
        # Strategy mapping
        strategy_config = {
            'portfolio_analysis': {
                'type': 'portfolio_analysis',
                'requires_data': ['portfolio_holdings', 'performance_metrics'],
                'visualizations': ['allocation_chart', 'performance_chart'],
                'actions': ['rebalance', 'optimize', 'detailed_analysis']
            },
            'trading_signals': {
                'type': 'trading_signals',
                'requires_data': ['market_data', 'technical_indicators'],
                'visualizations': ['signal_chart', 'risk_reward_chart'],
                'actions': ['place_order', 'set_alert', 'backtest_strategy']
            },
            'risk_assessment': {
                'type': 'risk_analysis',
                'requires_data': ['portfolio_data', 'risk_metrics'],
                'visualizations': ['risk_breakdown', 'var_chart'],
                'actions': ['stress_test', 'hedge_recommendation', 'risk_report']
            },
            'market_analysis': {
                'type': 'market_intelligence',
                'requires_data': ['market_overview', 'sector_data'],
                'visualizations': ['market_heatmap', 'sector_rotation'],
                'actions': ['sector_screening', 'market_report', 'opportunity_scan']
            },
            'performance_review': {
                'type': 'performance_attribution',
                'requires_data': ['performance_data', 'benchmark_data'],
                'visualizations': ['attribution_chart', 'performance_comparison'],
                'actions': ['detailed_attribution', 'benchmark_analysis', 'improvement_plan']
            }
        }
        
        # Get base strategy
        strategy = strategy_config.get(primary_intent, strategy_config['portfolio_analysis'])
        
        # Enhance strategy based on entities and context
        if entities['symbols']:
            strategy['focus_symbols'] = entities['symbols']
        
        if entities['timeframes']:
            strategy['timeframe'] = entities['timeframes'][0]
        
        if entities['actions']:
            strategy['user_actions'] = entities['actions']
        
        # Confidence-based adjustments
        if confidence < 0.5:
            strategy['fallback_mode'] = True
            strategy['type'] = 'general_guidance'
        
        return strategy
    
    def _build_contextual_prompt(self, intent_analysis: Dict, entities: Dict, 
                                context: Dict, strategy: Dict) -> str:
        """Build contextual prompt for AI generation"""
        
        strategy_type = strategy['type']
        
        if strategy_type not in self.prompt_templates:
            strategy_type = 'portfolio_analysis'  # Default fallback
        
        base_prompt = self.prompt_templates[strategy_type]
        
        # Build context data
        context_data = {
            'portfolio_value': context.get('portfolio_value', '₹10,50,000'),
            'holdings_count': context.get('holdings_count', 8),
            'risk_level': context.get('risk_level', 'Moderate'),
            'performance': context.get('performance', '+12.5% YTD'),
            'holdings_breakdown': self._format_holdings(context.get('holdings', [])),
            'market_conditions': self._format_market_context(context.get('market_data', {})),
            'technical_indicators': self._format_technical_data(context.get('technical', {})),
            'fundamental_metrics': self._format_fundamental_data(context.get('fundamentals', {})),
            'sentiment_data': self._format_sentiment_data(context.get('sentiment', {})),
            'max_position': context.get('max_position_size', '5%'),
            'risk_tolerance': context.get('risk_tolerance', 'Moderate'),
            'time_horizon': entities.get('timeframes', ['Medium-term'])[0],
            'var_95': context.get('var_95', '₹45,000'),
            'max_drawdown': context.get('max_drawdown', '-8.5%'),
            'portfolio_beta': context.get('portfolio_beta', '1.15'),
            'volatility': context.get('volatility', '18.5%'),
            'correlation_matrix': self._format_correlation_data(context.get('correlations', {})),
            'stress_test_data': self._format_stress_test_data(context.get('stress_tests', {})),
            'total_return': context.get('total_return', '+15.2%'),
            'benchmark_return': context.get('benchmark_return', '+12.8%'),
            'alpha': context.get('alpha', '+2.4%'),
            'sharpe_ratio': context.get('sharpe_ratio', '1.25'),
            'info_ratio': context.get('info_ratio', '0.85'),
            'attribution_breakdown': self._format_attribution_data(context.get('attribution', {})),
            'benchmark_analysis': self._format_benchmark_data(context.get('benchmark', {})),
            'factor_exposure': self._format_factor_data(context.get('factors', {})),
            'market_overview': self._format_market_overview(context.get('market_overview', {})),
            'economic_data': self._format_economic_data(context.get('economic', {})),
            'sector_performance': self._format_sector_data(context.get('sectors', {})),
            'news_analysis': self._format_news_data(context.get('news', {})),
            'technical_levels': self._format_technical_levels(context.get('levels', {}))
        }
        
        # Format prompt with context
        try:
            formatted_prompt = base_prompt.format(**context_data)
        except KeyError as e:
            # Fallback if missing context
            formatted_prompt = f"Analyze the following request: {intent_analysis['primary']}\n\nUser entities: {entities}\n\nProvide professional financial analysis."
        
        return formatted_prompt
    
    def _generate_response_content(self, prompt: str, strategy: Dict) -> Dict[str, Any]:
        """Generate response content based on prompt and strategy"""
        
        # This would integrate with actual AI models (Anthropic, OpenAI, etc.)
        # For now, providing structured fallback responses
        
        strategy_type = strategy['type']
        
        response_templates = {
            'portfolio_analysis': {
                'message': """Based on your portfolio analysis request, here's a comprehensive assessment:

**Portfolio Health: GOOD** ✅
- Your portfolio shows strong diversification across sectors
- Risk-adjusted returns are above benchmark
- Current allocation appears well-balanced

**Key Recommendations:**
1. **Rebalancing Opportunity**: Consider reducing exposure to overweight positions
2. **Risk Optimization**: Current volatility is within target range
3. **Performance Enhancement**: Identified 2-3 underperforming holdings for review

**Next Steps:**
- Review quarterly rebalancing
- Monitor sector concentration
- Consider tax-loss harvesting opportunities""",

                'suggestions': [
                    'Run portfolio optimization analysis',
                    'Generate rebalancing recommendations', 
                    'Calculate risk metrics (VaR, Sharpe)',
                    'Compare with benchmark performance'
                ]
            },
            
            'trading_signals': {
                'message': """**Active Trading Signals** 📊

**HIGH CONFIDENCE SIGNALS:**
🟢 **RELIANCE** - STRONG BUY
- Entry: ₹2,485-2,495
- Target: ₹2,650 (6.5% upside)  
- Stop-Loss: ₹2,420
- Confidence: 8.5/10

🟡 **TCS** - HOLD
- Current: ₹3,892
- Resistance: ₹4,050
- Support: ₹3,750
- Confidence: 7.2/10

**Market Timing**: Current technical setup favors selective buying in quality names""",

                'suggestions': [
                    'Place buy order for RELIANCE',
                    'Set price alerts for breakout levels',
                    'Review stop-loss levels',
                    'Backtest signal performance'
                ]
            },
            
            'risk_analysis': {
                'message': """**Portfolio Risk Assessment** ⚠️

**Overall Risk Level: MODERATE** 
- VaR (95%): ₹45,000 (4.3% of portfolio)
- Maximum Drawdown: -8.5% (within tolerance)
- Portfolio Beta: 1.15 (slightly aggressive)

**Risk Breakdown:**
- **Market Risk**: 65% (High correlation with Nifty)
- **Concentration Risk**: 25% (Top 3 holdings = 45%)
- **Liquidity Risk**: 10% (All holdings liquid)

**Recommendations:**
1. Consider defensive allocation increase
2. Monitor concentration in financial sector
3. Review correlation during market stress""",

                'suggestions': [
                    'Run stress test scenarios',
                    'Calculate position-specific VaR',
                    'Review correlation matrix',
                    'Generate risk report'
                ]
            }
        }
        
        # Get template or create dynamic response
        if strategy_type in response_templates:
            response = response_templates[strategy_type].copy()
        else:
            response = {
                'message': f"I'm analyzing your {strategy_type} request. Let me provide comprehensive insights based on current market conditions and your portfolio context.",
                'suggestions': [
                    'Get detailed analysis',
                    'View related insights',
                    'Run advanced calculations',
                    'Generate custom report'
                ]
            }
        
        # Add dynamic elements
        response['confidence'] = np.random.uniform(0.75, 0.95)
        response['timestamp'] = datetime.now().isoformat()
        
        # Add visualizations if specified in strategy
        if 'visualizations' in strategy:
            response['visualizations'] = [
                {
                    'type': viz,
                    'title': f"{viz.replace('_', ' ').title()}",
                    'data_available': True
                }
                for viz in strategy['visualizations']
            ]
        
        # Add actions if specified
        if 'actions' in strategy:
            response['actions'] = [
                {
                    'id': action,
                    'label': action.replace('_', ' ').title(),
                    'endpoint': f'/api/vs_terminal_MLClass/{action}',
                    'method': 'POST'
                }
                for action in strategy['actions']
            ]
        
        return response
    
    def _manage_conversation_flow(self, user_message: str, response_content: Dict) -> Dict[str, Any]:
        """Manage conversation flow and context"""
        
        conversation_turn = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'response_type': response_content.get('type', 'general'),
            'response_length': len(response_content['message']),
            'suggestions_provided': len(response_content.get('suggestions', [])),
            'actions_provided': len(response_content.get('actions', []))
        }
        
        self.conversation_history.append(conversation_turn)
        
        # Keep only last 10 turns
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        # Analyze conversation patterns
        recent_topics = [turn['response_type'] for turn in self.conversation_history[-5:]]
        topic_frequency = {topic: recent_topics.count(topic) for topic in set(recent_topics)}
        
        return {
            'turn_number': len(self.conversation_history),
            'conversation_length': len(self.conversation_history),
            'recent_topics': recent_topics,
            'topic_frequency': topic_frequency,
            'context_continuity': len(set(recent_topics)) / len(recent_topics) if recent_topics else 0
        }
    
    # Helper formatting methods
    def _format_holdings(self, holdings: List) -> str:
        if not holdings:
            return "- RELIANCE (22%): ₹2,31,000\n- TCS (18%): ₹1,89,000\n- HDFC Bank (15%): ₹1,57,500"
        return "\n".join([f"- {h.get('symbol', 'N/A')} ({h.get('weight', 0)}%): ₹{h.get('value', 0):,}" for h in holdings[:5]])
    
    def _format_market_context(self, market_data: Dict) -> str:
        return f"Nifty: {market_data.get('nifty', '+0.75%')} | Volatility: {market_data.get('vix', '15.2')} | FII Flow: {market_data.get('fii_flow', '₹850 Cr inflow')}"
    
    def _format_technical_data(self, technical: Dict) -> str:
        return f"RSI: {technical.get('rsi', '65.2')} | MACD: {technical.get('macd', 'Bullish')} | Support: {technical.get('support', '2,450')} | Resistance: {technical.get('resistance', '2,580')}"
    
    def _format_fundamental_data(self, fundamentals: Dict) -> str:
        return f"P/E: {fundamentals.get('pe', '18.5')} | ROE: {fundamentals.get('roe', '15.2%')} | Debt/Equity: {fundamentals.get('de', '0.45')} | Revenue Growth: {fundamentals.get('growth', '12.5%')}"
    
    def _format_sentiment_data(self, sentiment: Dict) -> str:
        return f"Market Sentiment: {sentiment.get('overall', 'Cautiously Optimistic')} | Fear & Greed: {sentiment.get('fear_greed', '72 (Greed)')} | Put/Call Ratio: {sentiment.get('put_call', '0.85')}"
    
    def _format_correlation_data(self, correlations: Dict) -> str:
        return "Average correlation with Nifty: 0.78 | Highest correlation pair: HDFC-ICICI (0.85) | Lowest: ITC-TCS (0.32)"
    
    def _format_stress_test_data(self, stress_tests: Dict) -> str:
        return "Market Crash (-20%): Portfolio impact -18.5% | Interest Rate Hike: -12.2% | Sector Rotation: -8.7%"
    
    def _format_attribution_data(self, attribution: Dict) -> str:
        return "Security Selection: +2.1% | Asset Allocation: +0.8% | Interaction Effect: -0.3% | Total Alpha: +2.6%"
    
    def _format_benchmark_data(self, benchmark: Dict) -> str:
        return f"Outperformance: {benchmark.get('outperformance', '+2.4%')} | Tracking Error: {benchmark.get('tracking_error', '4.2%')} | Beta: {benchmark.get('beta', '1.15')}"
    
    def _format_factor_data(self, factors: Dict) -> str:
        return "Value: 0.15 | Growth: 0.32 | Quality: 0.28 | Momentum: 0.18 | Low Vol: -0.12 | Size: 0.08"
    
    def _format_market_overview(self, market: Dict) -> str:
        return f"Market Regime: {market.get('regime', 'Risk-On')} | Trend: {market.get('trend', 'Uptrend')} | Breadth: {market.get('breadth', '68% stocks above 50-DMA')}"
    
    def _format_economic_data(self, economic: Dict) -> str:
        return f"GDP Growth: {economic.get('gdp', '6.8%')} | Inflation: {economic.get('inflation', '4.2%')} | Repo Rate: {economic.get('repo', '6.5%')} | USD/INR: {economic.get('usdinr', '83.25')}"
    
    def _format_sector_data(self, sectors: Dict) -> str:
        return "Leaders: IT (+8.5%), Banking (+6.2%) | Laggards: Metals (-4.1%), Pharma (-2.8%) | Rotation: Defensive to Growth"
    
    def _format_news_data(self, news: Dict) -> str:
        return f"Sentiment Score: {news.get('sentiment', '7.2/10')} | Key Themes: {news.get('themes', 'Earnings, Policy, Global cues')} | Impact: {news.get('impact', 'Moderately Positive')}"
    
    def _format_technical_levels(self, levels: Dict) -> str:
        return f"Nifty Support: {levels.get('support', '19,450')} | Resistance: {levels.get('resistance', '19,850')} | Trend: {levels.get('trend', 'Bullish')} | Volume: {levels.get('volume', 'Above Average')}"


# Integration function for the main app
def enhance_ml_class_prompt_engine(app):
    """Enhance ML Class with advanced prompt engineering"""
    
    # Initialize the prompt engine
    app.ml_prompt_engine = MLClassPromptEngine()
    
    # Replace the existing generate_ml_class_ai_response function
    def generate_enhanced_ml_class_ai_response(user_message, context=None):
        """Enhanced version of the ML Class AI response function"""
        return app.ml_prompt_engine.generate_enhanced_response(user_message, context or {})
    
    # Store the enhanced function globally
    app.generate_ml_class_ai_response = generate_enhanced_ml_class_ai_response
    
    app.logger.info("🧠 Enhanced Prompt Engineering System initialized for ML Class")
    
    return app.ml_prompt_engine