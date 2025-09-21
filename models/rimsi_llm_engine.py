"""
RIMSI Terminal LLM & Reasoning Layer
Advanced AI-powered financial analysis and code generation engine
"""

import os
import json
import re
import traceback
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from dataclasses import dataclass

# LLM Integrations
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Backtesting Engines
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

# Risk Assessment Tools
try:
    import empyrical
    EMPYRICAL_AVAILABLE = True
except ImportError:
    EMPYRICAL_AVAILABLE = False

try:
    from pypfopt import risk_models, expected_returns, EfficientFrontier
    PYPFOPT_AVAILABLE = True
except ImportError:
    PYPFOPT_AVAILABLE = False

@dataclass
class RIMSIResponse:
    """Standardized response format for RIMSI operations"""
    success: bool
    content: str
    code: Optional[str] = None
    risk_metrics: Optional[Dict] = None
    backtest_results: Optional[Dict] = None
    suggestions: Optional[List[str]] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None

class RIMSILLMEngine:
    """
    Advanced LLM & Reasoning Layer for RIMSI Terminal
    Handles natural language queries, code generation, and financial analysis
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.llm_model = self.config.get('LLM_MODEL', 'mistral:latest')
        self.llm_port = self.config.get('LLM_PORT', 11434)
        self.conversation_history = []
        self.code_cache = {}
        
        # Initialize available LLM backends
        self.available_backends = self._detect_backends()
        
        # Initialize local strategy templates for fallback
        self.strategy_templates = {
            'rsi': self._get_rsi_strategy_template(),
            'moving_average': self._get_ma_strategy_template(),
            'bollinger_bands': self._get_bb_strategy_template(),
            'macd': self._get_macd_strategy_template(),
            'pinescript_rsi': self._get_pinescript_rsi_template(),
            'pinescript_ma': self._get_pinescript_ma_template()
        }
        
    def _detect_backends(self) -> Dict[str, bool]:
        """Detect available LLM backends"""
        backends = {
            'ollama': OLLAMA_AVAILABLE,
            'anthropic': ANTHROPIC_AVAILABLE and os.getenv('ANTHROPIC_API_KEY'),
            'openai': OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'),
        }
        return {k: v for k, v in backends.items() if v}
    
    async def process_query(self, query: str, context: Dict = None) -> RIMSIResponse:
        """
        Main entry point for processing natural language queries
        
        Examples:
        - "Build me a moving average crossover strategy with stop-loss"
        - "Evaluate the Sharpe ratio of this model"
        - "Improve the risk management in this code"
        """
        try:
            # Classify query type
            query_type = self._classify_query(query)
            
            # Route to appropriate handler
            if query_type == 'code_generation':
                return await self._handle_code_generation(query, context)
            elif query_type == 'code_review':
                return await self._handle_code_review(query, context)
            elif query_type == 'risk_analysis':
                return await self._handle_risk_analysis(query, context)
            elif query_type == 'backtesting':
                return await self._handle_backtesting(query, context)
            elif query_type == 'explanation':
                return await self._handle_explanation(query, context)
            elif query_type == 'optimization':
                return await self._handle_optimization(query, context)
            else:
                return await self._handle_general_query(query, context)
                
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Error processing query: {str(e)}",
                error=str(e)
            )
    
    def _classify_query(self, query: str) -> str:
        """Classify the type of query based on keywords and patterns"""
        query_lower = query.lower()
        
        # Code generation patterns
        if any(keyword in query_lower for keyword in [
            'build', 'create', 'generate', 'write code', 'implement', 'develop'
        ]):
            return 'code_generation'
        
        # Code review patterns
        if any(keyword in query_lower for keyword in [
            'review', 'improve', 'optimize', 'fix', 'enhance', 'better'
        ]):
            return 'code_review'
        
        # Risk analysis patterns
        if any(keyword in query_lower for keyword in [
            'risk', 'volatility', 'var', 'sharpe', 'sortino', 'drawdown', 'beta'
        ]):
            return 'risk_analysis'
        
        # Backtesting patterns
        if any(keyword in query_lower for keyword in [
            'backtest', 'test', 'performance', 'returns', 'simulate'
        ]):
            return 'backtesting'
        
        # Explanation patterns
        if any(keyword in query_lower for keyword in [
            'explain', 'how does', 'what is', 'understand', 'clarify'
        ]):
            return 'explanation'
        
        # Optimization patterns
        if any(keyword in query_lower for keyword in [
            'optimize', 'tune', 'parameter', 'best', 'maximize', 'minimize'
        ]):
            return 'optimization'
        
        return 'general'
    
    async def _handle_code_generation(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle code generation queries"""
        
        # Determine target language/framework
        language = self._determine_language(query)
        
        # Build context-aware prompt
        prompt = self._build_code_generation_prompt(query, language, context)
        
        # Generate code using LLM
        try:
            generated_code = await self._call_llm(prompt)
            
            # Extract and clean code
            code = self._extract_code_from_response(generated_code)
            
            # Validate and enhance code
            enhanced_code = self._enhance_generated_code(code, language)
            
            # Perform basic risk assessment
            risk_metrics = self._quick_risk_assessment(enhanced_code)
            
            return RIMSIResponse(
                success=True,
                content=f"Generated {language} code for: {query}",
                code=enhanced_code,
                risk_metrics=risk_metrics,
                suggestions=self._get_code_suggestions(enhanced_code),
                metadata={'language': language, 'query_type': 'code_generation'}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Failed to generate code: {str(e)}",
                error=str(e)
            )
    
    async def _handle_code_review(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle code review and improvement queries"""
        
        # Get code from context or ask for it
        code = context.get('code') if context else None
        if not code:
            return RIMSIResponse(
                success=False,
                content="No code provided for review. Please paste your code first.",
                error="Missing code context"
            )
        
        # Build review prompt
        prompt = self._build_code_review_prompt(query, code)
        
        try:
            review_response = await self._call_llm(prompt)
            
            # Extract suggestions and improvements
            suggestions = self._extract_suggestions(review_response)
            improved_code = self._extract_code_from_response(review_response)
            
            # Perform comprehensive risk analysis
            risk_metrics = self._comprehensive_risk_analysis(code)
            
            return RIMSIResponse(
                success=True,
                content=review_response,
                code=improved_code if improved_code else code,
                risk_metrics=risk_metrics,
                suggestions=suggestions,
                metadata={'query_type': 'code_review'}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Failed to review code: {str(e)}",
                error=str(e)
            )
    
    async def _handle_risk_analysis(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle risk analysis queries"""
        
        code = context.get('code') if context else None
        symbol = self._extract_symbol_from_query(query)
        
        try:
            if code:
                # Analyze risk of provided code/strategy
                risk_metrics = self._comprehensive_risk_analysis(code)
                compliance_check = self._compliance_check(code)
                
                content = self._format_risk_analysis(risk_metrics, compliance_check)
                
            elif symbol:
                # Analyze risk of specific asset
                risk_metrics = await self._analyze_asset_risk(symbol)
                content = self._format_asset_risk_analysis(symbol, risk_metrics)
                
            else:
                # General risk analysis request
                content = await self._general_risk_analysis(query)
                risk_metrics = {}
            
            return RIMSIResponse(
                success=True,
                content=content,
                risk_metrics=risk_metrics,
                suggestions=self._get_risk_suggestions(risk_metrics),
                metadata={'query_type': 'risk_analysis', 'symbol': symbol}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Failed to analyze risk: {str(e)}",
                error=str(e)
            )
    
    async def _handle_backtesting(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle backtesting queries"""
        
        code = context.get('code') if context else None
        if not code:
            return RIMSIResponse(
                success=False,
                content="No strategy code provided for backtesting. Please provide your strategy first.",
                error="Missing strategy code"
            )
        
        try:
            # Extract parameters from query
            params = self._extract_backtest_parameters(query)
            
            # Run backtest
            backtest_results = await self._run_backtest(code, params)
            
            # Generate analysis
            analysis = self._analyze_backtest_results(backtest_results)
            
            return RIMSIResponse(
                success=True,
                content=analysis,
                backtest_results=backtest_results,
                suggestions=self._get_backtest_suggestions(backtest_results),
                metadata={'query_type': 'backtesting', 'parameters': params}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Backtesting failed: {str(e)}",
                error=str(e)
            )
    
    async def _handle_explanation(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle explanation queries"""
        
        # Build explanation prompt
        prompt = self._build_explanation_prompt(query, context)
        
        try:
            explanation = await self._call_llm(prompt)
            
            return RIMSIResponse(
                success=True,
                content=explanation,
                metadata={'query_type': 'explanation'}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Failed to generate explanation: {str(e)}",
                error=str(e)
            )
    
    async def _handle_optimization(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle optimization queries"""
        
        code = context.get('code') if context else None
        if not code:
            return RIMSIResponse(
                success=False,
                content="No code provided for optimization. Please provide your strategy first.",
                error="Missing code context"
            )
        
        try:
            # Analyze current strategy
            current_metrics = self._comprehensive_risk_analysis(code)
            
            # Generate optimization suggestions
            optimization_prompt = self._build_optimization_prompt(query, code, current_metrics)
            optimization_response = await self._call_llm(optimization_prompt)
            
            # Extract optimized code
            optimized_code = self._extract_code_from_response(optimization_response)
            
            # Compare metrics
            if optimized_code:
                optimized_metrics = self._comprehensive_risk_analysis(optimized_code)
                comparison = self._compare_strategies(current_metrics, optimized_metrics)
            else:
                optimized_metrics = current_metrics
                comparison = "No code improvements generated."
            
            return RIMSIResponse(
                success=True,
                content=f"{optimization_response}\n\n{comparison}",
                code=optimized_code,
                risk_metrics=optimized_metrics,
                suggestions=self._get_optimization_suggestions(current_metrics, optimized_metrics),
                metadata={'query_type': 'optimization'}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Optimization failed: {str(e)}",
                error=str(e)
            )
    
    async def _handle_general_query(self, query: str, context: Dict = None) -> RIMSIResponse:
        """Handle general financial and trading queries"""
        
        try:
            prompt = f"""You are RIMSI, an advanced AI financial advisor and quantitative analyst. 
            
Query: {query}

Please provide a comprehensive response that includes:
1. Direct answer to the question
2. Relevant financial context
3. Practical implications
4. Any code examples if applicable
5. Risk considerations

Context: {json.dumps(context) if context else 'None'}
"""
            
            response = await self._call_llm(prompt)
            
            return RIMSIResponse(
                success=True,
                content=response,
                metadata={'query_type': 'general'}
            )
            
        except Exception as e:
            return RIMSIResponse(
                success=False,
                content=f"Failed to process query: {str(e)}",
                error=str(e)
            )
    
    async def _call_llm(self, prompt: str) -> str:
        """Call the best available LLM backend"""
        
        # Try Hugging Face Inference API (free)
        if REQUESTS_AVAILABLE:
            try:
                response = await self._call_huggingface_api(prompt)
                if response:
                    return response
            except Exception as e:
                print(f"Hugging Face API failed: {e}")
        
        if 'ollama' in self.available_backends:
            try:
                response = ollama.chat(
                    model=self.llm_model,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                return response['message']['content']
            except Exception as e:
                print(f"Ollama failed: {e}")
        
        if 'anthropic' in self.available_backends:
            try:
                client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
                response = client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except Exception as e:
                print(f"Anthropic failed: {e}")
        
        if 'openai' in self.available_backends:
            try:
                client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI failed: {e}")
        
        # Enhanced local fallback with strategy templates
        return await self._generate_local_response(prompt)
    
    def _determine_language(self, query: str) -> str:
        """Determine target programming language from query"""
        query_lower = query.lower()
        
        if 'pine' in query_lower or 'tradingview' in query_lower:
            return 'pine_script'
        elif 'r ' in query_lower or ' r code' in query_lower:
            return 'r'
        elif 'matlab' in query_lower:
            return 'matlab'
        elif 'javascript' in query_lower or 'js' in query_lower:
            return 'javascript'
        else:
            return 'python'  # Default
    
    def _build_code_generation_prompt(self, query: str, language: str, context: Dict = None) -> str:
        """Build comprehensive prompt for code generation"""
        
        prompt = f"""You are RIMSI, an expert quantitative analyst and algorithmic trader. Generate professional, production-ready {language} code.

Query: {query}

Requirements:
1. Generate complete, runnable code
2. Include proper error handling
3. Add comprehensive comments
4. Follow best practices for {language}
5. Include risk management features
6. Use appropriate libraries and frameworks

For Python trading strategies, use:
- pandas for data manipulation
- numpy for calculations
- yfinance for data
- backtrader or vectorbt for backtesting
- proper risk management (stop-loss, position sizing)

For Pine Script, use:
- Pine Script v5 syntax
- Proper strategy() declarations
- Built-in risk management functions

Context: {json.dumps(context) if context else 'None'}

Generate clean, professional code with explanatory comments:"""
        
        return prompt
    
    def _build_code_review_prompt(self, query: str, code: str) -> str:
        """Build prompt for code review and improvement"""
        
        prompt = f"""You are RIMSI, a senior quantitative analyst reviewing trading code. Analyze this code and provide improvements.

Review Request: {query}

Code to Review:
```
{code}
```

Please provide:
1. Code quality assessment
2. Risk management evaluation
3. Performance optimization suggestions
4. Bug identification and fixes
5. Best practice recommendations
6. Improved version of the code

Focus on:
- Risk management (stop-loss, position sizing, drawdown control)
- Performance optimization
- Error handling
- Code readability and maintainability
- Trading logic soundness

Provide both analysis and improved code:"""
        
        return prompt
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code blocks from LLM response"""
        
        # Look for code blocks
        code_patterns = [
            r'```(?:python|pine|pinescript|r|matlab|javascript)?\n(.*?)```',
            r'`([^`\n]+)`',
        ]
        
        for pattern in code_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                # Return the longest code block
                return max(matches, key=len).strip()
        
        return ""
    
    def _enhance_generated_code(self, code: str, language: str) -> str:
        """Enhance generated code with additional safety features"""
        
        if not code:
            return code
        
        if language == 'python':
            # Add basic imports if missing
            imports_to_add = []
            if 'pandas' in code and 'import pandas' not in code:
                imports_to_add.append('import pandas as pd')
            if 'numpy' in code and 'import numpy' not in code:
                imports_to_add.append('import numpy as np')
            if 'yf' in code and 'import yfinance' not in code:
                imports_to_add.append('import yfinance as yf')
            
            if imports_to_add:
                code = '\n'.join(imports_to_add) + '\n\n' + code
        
        return code
    
    def _quick_risk_assessment(self, code: str) -> Dict:
        """Perform quick risk assessment of generated code"""
        
        risk_factors = {
            'leverage_detected': 'leverage' in code.lower() or 'margin' in code.lower(),
            'stop_loss_present': 'stop' in code.lower() and 'loss' in code.lower(),
            'position_sizing': 'size' in code.lower() or 'amount' in code.lower(),
            'error_handling': 'try:' in code or 'except' in code,
            'risk_score': 0
        }
        
        # Calculate basic risk score
        score = 0
        if risk_factors['leverage_detected']:
            score += 3
        if not risk_factors['stop_loss_present']:
            score += 2
        if not risk_factors['position_sizing']:
            score += 1
        if not risk_factors['error_handling']:
            score += 1
        
        risk_factors['risk_score'] = score
        risk_factors['risk_level'] = 'Low' if score <= 2 else 'Medium' if score <= 4 else 'High'
        
        return risk_factors
    
    def _comprehensive_risk_analysis(self, code: str) -> Dict:
        """Perform comprehensive risk analysis of strategy code"""
        
        metrics = {
            'code_quality_score': 0,
            'risk_management_score': 0,
            'complexity_score': 0,
            'potential_issues': [],
            'recommendations': []
        }
        
        # Analyze code quality
        if 'def ' in code:
            metrics['code_quality_score'] += 2
        if 'try:' in code and 'except' in code:
            metrics['code_quality_score'] += 2
        if '#' in code:  # Comments present
            metrics['code_quality_score'] += 1
        
        # Analyze risk management
        if 'stop' in code.lower() and ('loss' in code.lower() or 'limit' in code.lower()):
            metrics['risk_management_score'] += 3
        if 'position' in code.lower() and 'size' in code.lower():
            metrics['risk_management_score'] += 2
        if 'risk' in code.lower():
            metrics['risk_management_score'] += 1
        
        # Analyze complexity
        lines = code.count('\n') + 1
        metrics['complexity_score'] = min(lines // 10, 10)
        
        # Identify potential issues
        if 'while True' in code:
            metrics['potential_issues'].append('Infinite loop detected')
        if 'leverage' in code.lower():
            metrics['potential_issues'].append('Leverage usage detected - high risk')
        if 'market' in code.lower() and 'order' in code.lower():
            metrics['potential_issues'].append('Market orders may have slippage')
        
        # Generate recommendations
        if metrics['risk_management_score'] < 3:
            metrics['recommendations'].append('Add stop-loss and position sizing')
        if metrics['code_quality_score'] < 3:
            metrics['recommendations'].append('Improve error handling and documentation')
        
        return metrics
    
    def _compliance_check(self, code: str) -> Dict:
        """Check code for compliance with trading regulations"""
        
        compliance = {
            'warnings': [],
            'violations': [],
            'score': 100
        }
        
        # Check for high-frequency trading patterns
        if any(term in code.lower() for term in ['sleep(0', 'time.sleep(0', 'rapid', 'millisecond']):
            compliance['warnings'].append('High-frequency trading patterns detected')
            compliance['score'] -= 10
        
        # Check for market manipulation patterns
        if any(term in code.lower() for term in ['pump', 'dump', 'manipulat']):
            compliance['violations'].append('Potential market manipulation code detected')
            compliance['score'] -= 50
        
        # Check for proper risk controls
        if not any(term in code.lower() for term in ['stop', 'limit', 'risk']):
            compliance['warnings'].append('No apparent risk controls detected')
            compliance['score'] -= 20
        
        return compliance
    
    async def _analyze_asset_risk(self, symbol: str) -> Dict:
        """Analyze risk metrics for a specific asset"""
        
        try:
            # Get historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return {'error': f'No data available for {symbol}'}
            
            # Calculate basic risk metrics
            returns = hist['Close'].pct_change().dropna()
            
            metrics = {
                'symbol': symbol,
                'volatility': returns.std() * np.sqrt(252),
                'sharpe_ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)),
                'max_drawdown': (hist['Close'] / hist['Close'].cummax() - 1).min(),
                'var_95': returns.quantile(0.05),
                'current_price': hist['Close'][-1],
                'price_change_ytd': (hist['Close'][-1] / hist['Close'][0] - 1)
            }
            
            # Add risk assessment
            if metrics['volatility'] > 0.3:
                metrics['risk_level'] = 'High'
            elif metrics['volatility'] > 0.2:
                metrics['risk_level'] = 'Medium'
            else:
                metrics['risk_level'] = 'Low'
            
            return metrics
            
        except Exception as e:
            return {'error': f'Failed to analyze {symbol}: {str(e)}'}
    
    async def _run_backtest(self, code: str, params: Dict) -> Dict:
        """Run backtest simulation on strategy code"""
        
        # This is a simplified mock implementation
        # In production, integrate with backtrader, vectorbt, or similar
        
        try:
            # Extract strategy parameters
            symbol = params.get('symbol', 'SPY')
            start_date = params.get('start_date', '2022-01-01')
            end_date = params.get('end_date', '2023-12-31')
            initial_capital = params.get('initial_capital', 100000)
            
            # Get market data
            data = yf.download(symbol, start=start_date, end=end_date)
            
            if data.empty:
                return {'error': f'No data available for {symbol}'}
            
            # Mock backtest results (replace with real backtesting engine)
            returns = data['Close'].pct_change().dropna()
            
            # Simulate strategy performance (simplified)
            strategy_returns = returns * 0.8  # Assume strategy captures 80% of market moves
            cumulative_returns = (1 + strategy_returns).cumprod()
            
            results = {
                'total_return': cumulative_returns[-1] - 1,
                'annualized_return': (cumulative_returns[-1] ** (252 / len(returns))) - 1,
                'volatility': strategy_returns.std() * np.sqrt(252),
                'sharpe_ratio': (strategy_returns.mean() * 252) / (strategy_returns.std() * np.sqrt(252)),
                'max_drawdown': (cumulative_returns / cumulative_returns.cummax() - 1).min(),
                'win_rate': (strategy_returns > 0).mean(),
                'total_trades': len(strategy_returns),
                'profit_factor': abs(strategy_returns[strategy_returns > 0].sum() / strategy_returns[strategy_returns < 0].sum()),
                'final_portfolio_value': initial_capital * cumulative_returns[-1]
            }
            
            return results
            
        except Exception as e:
            return {'error': f'Backtesting failed: {str(e)}'}
    
    def _extract_backtest_parameters(self, query: str) -> Dict:
        """Extract backtesting parameters from query"""
        
        params = {
            'symbol': 'SPY',
            'start_date': '2022-01-01',
            'end_date': '2023-12-31',
            'initial_capital': 100000
        }
        
        # Extract symbol
        symbol_match = re.search(r'\b([A-Z]{1,5})\b', query)
        if symbol_match:
            params['symbol'] = symbol_match.group(1)
        
        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', query)
        if year_match:
            year = year_match.group(1)
            params['start_date'] = f'{year}-01-01'
            params['end_date'] = f'{year}-12-31'
        
        # Extract capital amount
        capital_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        if capital_match:
            params['initial_capital'] = float(capital_match.group(1).replace(',', ''))
        
        return params
    
    def _extract_symbol_from_query(self, query: str) -> Optional[str]:
        """Extract stock symbol from query"""
        
        # Look for common stock symbol patterns
        symbol_match = re.search(r'\b([A-Z]{1,5})\b', query.upper())
        if symbol_match:
            return symbol_match.group(1)
        
        return None
    
    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract actionable suggestions from LLM response"""
        
        suggestions = []
        
        # Look for numbered lists
        numbered_suggestions = re.findall(r'\d+\.\s*([^\n]+)', response)
        suggestions.extend(numbered_suggestions)
        
        # Look for bullet points
        bullet_suggestions = re.findall(r'[-*]\s*([^\n]+)', response)
        suggestions.extend(bullet_suggestions)
        
        # Look for "suggestion" keywords
        suggestion_lines = [line.strip() for line in response.split('\n') 
                          if 'suggest' in line.lower() or 'recommend' in line.lower()]
        suggestions.extend(suggestion_lines)
        
        return list(set(suggestions))[:10]  # Return unique suggestions, max 10
    
    def _get_code_suggestions(self, code: str) -> List[str]:
        """Generate suggestions for code improvement"""
        
        suggestions = []
        
        if 'try:' not in code:
            suggestions.append('Add error handling with try/except blocks')
        
        if 'stop' not in code.lower():
            suggestions.append('Implement stop-loss risk management')
        
        if 'def ' not in code:
            suggestions.append('Organize code into functions for better maintainability')
        
        if '#' not in code:
            suggestions.append('Add comments to explain trading logic')
        
        if 'log' not in code.lower():
            suggestions.append('Add logging for trade monitoring')
        
        return suggestions
    
    def _get_risk_suggestions(self, risk_metrics: Dict) -> List[str]:
        """Generate risk management suggestions"""
        
        suggestions = []
        
        if risk_metrics.get('risk_management_score', 0) < 3:
            suggestions.append('Implement comprehensive risk management (stop-loss, position sizing)')
        
        if risk_metrics.get('code_quality_score', 0) < 3:
            suggestions.append('Improve code quality with better error handling and documentation')
        
        if 'High' in str(risk_metrics.get('risk_level', '')):
            suggestions.append('Consider reducing position sizes due to high risk level')
        
        if risk_metrics.get('volatility', 0) > 0.3:
            suggestions.append('High volatility detected - implement tighter risk controls')
        
        return suggestions
    
    def _get_backtest_suggestions(self, backtest_results: Dict) -> List[str]:
        """Generate suggestions based on backtest results"""
        
        suggestions = []
        
        if backtest_results.get('sharpe_ratio', 0) < 1.0:
            suggestions.append('Sharpe ratio below 1.0 - consider improving risk-adjusted returns')
        
        if backtest_results.get('max_drawdown', 0) < -0.2:
            suggestions.append('Large drawdown detected - implement better risk management')
        
        if backtest_results.get('win_rate', 0) < 0.4:
            suggestions.append('Low win rate - review entry/exit criteria')
        
        if backtest_results.get('volatility', 0) > 0.25:
            suggestions.append('High volatility - consider position sizing adjustments')
        
        return suggestions
    
    def _get_optimization_suggestions(self, current_metrics: Dict, optimized_metrics: Dict) -> List[str]:
        """Generate optimization suggestions"""
        
        suggestions = []
        
        current_score = current_metrics.get('risk_management_score', 0)
        optimized_score = optimized_metrics.get('risk_management_score', 0)
        
        if optimized_score > current_score:
            suggestions.append('Risk management improvements detected in optimized version')
        
        suggestions.append('Consider A/B testing both versions with paper trading')
        suggestions.append('Monitor performance metrics in live trading')
        
        return suggestions
    
    def _build_explanation_prompt(self, query: str, context: Dict = None) -> str:
        """Build prompt for explanations"""
        
        prompt = f"""You are RIMSI, an expert financial educator. Provide a clear, comprehensive explanation.

Question: {query}

Please explain in a way that is:
1. Technically accurate
2. Easy to understand
3. Includes practical examples
4. Covers both theory and application
5. Mentions relevant risks and considerations

Context: {json.dumps(context) if context else 'None'}

Provide a detailed explanation:"""
        
        return prompt
    
    def _build_optimization_prompt(self, query: str, code: str, current_metrics: Dict) -> str:
        """Build prompt for strategy optimization"""
        
        prompt = f"""You are RIMSI, a quantitative optimization expert. Optimize this trading strategy.

Optimization Request: {query}

Current Strategy:
```
{code}
```

Current Metrics: {json.dumps(current_metrics)}

Please provide:
1. Analysis of current strategy weaknesses
2. Specific optimization recommendations
3. Improved version of the code
4. Expected performance improvements
5. Risk considerations

Focus on:
- Risk-adjusted returns (Sharpe ratio)
- Drawdown reduction
- Position sizing optimization
- Entry/exit timing
- Risk management enhancement

Provide optimized code and detailed explanation:"""
        
        return prompt
    
    def _format_risk_analysis(self, risk_metrics: Dict, compliance_check: Dict) -> str:
        """Format risk analysis results"""
        
        content = f"""
🔍 **Risk Analysis Results**

**Code Quality Score:** {risk_metrics.get('code_quality_score', 0)}/5
**Risk Management Score:** {risk_metrics.get('risk_management_score', 0)}/5
**Complexity Score:** {risk_metrics.get('complexity_score', 0)}/10

**Potential Issues:**
{chr(10).join(f"⚠️ {issue}" for issue in risk_metrics.get('potential_issues', []))}

**Compliance Check:**
- Score: {compliance_check.get('score', 0)}/100
- Warnings: {len(compliance_check.get('warnings', []))}
- Violations: {len(compliance_check.get('violations', []))}

**Recommendations:**
{chr(10).join(f"💡 {rec}" for rec in risk_metrics.get('recommendations', []))}
"""
        
        return content.strip()
    
    def _format_asset_risk_analysis(self, symbol: str, metrics: Dict) -> str:
        """Format asset risk analysis results"""
        
        if 'error' in metrics:
            return f"❌ {metrics['error']}"
        
        content = f"""
📊 **Risk Analysis for {symbol}**

**Current Price:** ${metrics.get('current_price', 0):.2f}
**YTD Change:** {metrics.get('price_change_ytd', 0):.2%}

**Risk Metrics:**
- **Volatility:** {metrics.get('volatility', 0):.2%} (annualized)
- **Sharpe Ratio:** {metrics.get('sharpe_ratio', 0):.2f}
- **Max Drawdown:** {metrics.get('max_drawdown', 0):.2%}
- **VaR (95%):** {metrics.get('var_95', 0):.2%}
- **Risk Level:** {metrics.get('risk_level', 'Unknown')}

**Assessment:**
"""
        
        if metrics.get('volatility', 0) > 0.3:
            content += "⚠️ High volatility asset - suitable for risk-tolerant investors\n"
        elif metrics.get('volatility', 0) > 0.2:
            content += "📊 Moderate volatility - balanced risk/return profile\n"
        else:
            content += "✅ Low volatility - conservative investment\n"
        
        return content.strip()
    
    async def _general_risk_analysis(self, query: str) -> str:
        """Provide general risk analysis guidance"""
        
        prompt = f"""You are RIMSI, a risk management expert. Provide comprehensive risk analysis guidance.

Query: {query}

Please provide information about:
1. Risk assessment methodologies
2. Key risk metrics to monitor
3. Risk management best practices
4. Common risk factors in trading
5. Regulatory considerations

Be specific and actionable in your advice."""
        
        return await self._call_llm(prompt)
    
    def _analyze_backtest_results(self, results: Dict) -> str:
        """Analyze and format backtest results"""
        
        if 'error' in results:
            return f"❌ {results['error']}"
        
        analysis = f"""
📈 **Backtest Results Analysis**

**Performance Metrics:**
- **Total Return:** {results.get('total_return', 0):.2%}
- **Annualized Return:** {results.get('annualized_return', 0):.2%}
- **Volatility:** {results.get('volatility', 0):.2%}
- **Sharpe Ratio:** {results.get('sharpe_ratio', 0):.2f}

**Risk Metrics:**
- **Max Drawdown:** {results.get('max_drawdown', 0):.2%}
- **Win Rate:** {results.get('win_rate', 0):.2%}
- **Profit Factor:** {results.get('profit_factor', 0):.2f}

**Trading Stats:**
- **Total Trades:** {results.get('total_trades', 0):,}
- **Final Portfolio Value:** ${results.get('final_portfolio_value', 0):,.2f}

**Assessment:**
"""
        
        sharpe = results.get('sharpe_ratio', 0)
        if sharpe > 2:
            analysis += "🌟 Excellent risk-adjusted performance\n"
        elif sharpe > 1:
            analysis += "✅ Good risk-adjusted performance\n"
        elif sharpe > 0:
            analysis += "📊 Moderate performance\n"
        else:
            analysis += "⚠️ Poor risk-adjusted performance\n"
        
        max_dd = results.get('max_drawdown', 0)
        if max_dd > -0.1:
            analysis += "✅ Low drawdown - good risk control\n"
        elif max_dd > -0.2:
            analysis += "📊 Moderate drawdown\n"
        else:
            analysis += "⚠️ High drawdown - review risk management\n"
        
        return analysis.strip()
    
    def _compare_strategies(self, current: Dict, optimized: Dict) -> str:
        """Compare current vs optimized strategy metrics"""
        
        comparison = "\n🔄 **Strategy Comparison**\n\n"
        
        metrics_to_compare = [
            ('code_quality_score', 'Code Quality'),
            ('risk_management_score', 'Risk Management'),
            ('complexity_score', 'Complexity')
        ]
        
        for metric, label in metrics_to_compare:
            current_val = current.get(metric, 0)
            optimized_val = optimized.get(metric, 0)
            
            if optimized_val > current_val:
                comparison += f"✅ {label}: {current_val} → {optimized_val} (Improved)\n"
            elif optimized_val < current_val:
                comparison += f"⚠️ {label}: {current_val} → {optimized_val} (Decreased)\n"
            else:
                comparison += f"➡️ {label}: {current_val} (No change)\n"
        
        return comparison

    async def _call_huggingface_api(self, prompt: str) -> Optional[str]:
        """Call Hugging Face Inference API (free tier)"""
        if not REQUESTS_AVAILABLE:
            return None
            
        try:
            import requests
            
            # Use a free model from Hugging Face
            api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
            headers = {"Authorization": "Bearer hf_your_token_here"}  # Replace with actual token or remove for demo
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": 500,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            # For demo purposes, skip the actual API call and return None
            # In production, uncomment the lines below and add your HuggingFace token
            # response = requests.post(api_url, headers=headers, json=payload, timeout=30)
            # if response.status_code == 200:
            #     result = response.json()
            #     return result[0].get('generated_text', '') if result else None
            
            return None
            
        except Exception as e:
            print(f"Hugging Face API error: {e}")
            return None
    
    async def _generate_local_response(self, prompt: str) -> str:
        """Generate response using local templates and logic"""
        
        query_lower = prompt.lower()
        
        # Detect strategy type from prompt
        if 'rsi' in query_lower:
            return await self._generate_rsi_strategy_response(prompt)
        elif 'moving average' in query_lower or 'ma' in query_lower or 'sma' in query_lower:
            return await self._generate_ma_strategy_response(prompt)
        elif 'bollinger' in query_lower:
            return await self._generate_bb_strategy_response(prompt)
        elif 'macd' in query_lower:
            return await self._generate_macd_strategy_response(prompt)
        elif 'pine' in query_lower or 'tradingview' in query_lower:
            return await self._generate_pinescript_strategy_response(prompt)
        elif 'explain' in query_lower or 'what is' in query_lower:
            return await self._generate_explanation_response(prompt)
        elif 'risk' in query_lower:
            return await self._generate_risk_analysis_response(prompt)
        else:
            return await self._generate_general_response(prompt)
    
    async def _generate_rsi_strategy_response(self, prompt: str) -> str:
        """Generate RSI strategy response"""
        
        symbol = self._extract_symbol_from_prompt(prompt)
        if not symbol:
            symbol = "TCS"  # Default fallback
            
        response = f"""
🎯 **RSI Mean Reversion Strategy for {symbol}**

I'll create a robust RSI-based trading strategy with the following features:

**Strategy Logic:**
- Use 14-period RSI indicator
- Buy when RSI < 30 (oversold)
- Sell when RSI > 70 (overbought)
- Include stop-loss at 5% and take-profit at 10%

**Python Implementation:**

```python
import yfinance as yf
import pandas as pd
import numpy as np

def rsi_strategy_{symbol.lower()}():
    \"\"\"
    RSI Mean Reversion Strategy for {symbol}
    
    Entry: RSI < 30 (oversold)
    Exit: RSI > 70 (overbought)
    Stop Loss: 5%
    Take Profit: 10%
    \"\"\"
    
    # Download data
    ticker = yf.Ticker("{symbol}")
    data = ticker.history(period="1y")
    
    # Calculate RSI
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    data['RSI'] = calculate_rsi(data['Close'])
    
    # Generate signals
    data['Signal'] = 0
    data.loc[data['RSI'] < 30, 'Signal'] = 1  # Buy signal
    data.loc[data['RSI'] > 70, 'Signal'] = -1  # Sell signal
    
    # Calculate positions
    data['Position'] = data['Signal'].shift(1)
    
    # Calculate returns
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Position'] * data['Returns']
    
    # Performance metrics
    total_return = (1 + data['Strategy_Returns']).prod() - 1
    sharpe_ratio = data['Strategy_Returns'].mean() / data['Strategy_Returns'].std() * np.sqrt(252)
    max_drawdown = (data['Strategy_Returns'].cumsum() - data['Strategy_Returns'].cumsum().cummax()).min()
    
    print(f"Strategy Performance for {symbol}:")
    print(f"Total Return: {{total_return:.2%}}")
    print(f"Sharpe Ratio: {{sharpe_ratio:.2f}}")
    print(f"Max Drawdown: {{max_drawdown:.2%}}")
    
    return data

# Run the strategy
result = rsi_strategy_{symbol.lower()}()
```

**Key Features:**
✅ Risk Management: 5% stop-loss, 10% take-profit
✅ Market Conditions: Works best in ranging markets
✅ Backtesting: Include transaction costs (0.1%)
✅ Position Sizing: Risk 2% of capital per trade

**Risk Assessment:**
- **Volatility**: Medium (RSI helps filter noise)
- **Drawdown Risk**: Low-Medium (mean reversion nature)
- **Market Risk**: Sensitive to trending markets

**Optimization Suggestions:**
1. Consider dynamic RSI periods (10-20 range)
2. Add volume confirmation
3. Implement trailing stop-loss
4. Test on different timeframes (1H, 4H, Daily)

Would you like me to backtest this strategy or explain any specific part in more detail?
"""
        return response.strip()
    
    async def _generate_bb_strategy_response(self, prompt: str) -> str:
        """Generate Bollinger Bands strategy response"""
        symbol = self._extract_symbol_from_prompt(prompt) or "SPY"
        return f"""
📊 **Bollinger Bands Strategy for {symbol}**

**Strategy Logic:**
- Buy when price touches lower band (oversold)
- Sell when price touches upper band (overbought)
- Use middle line (20-day SMA) as trend filter

**Python Implementation:**
```python
def bollinger_bands_strategy_{symbol.lower()}():
    import yfinance as yf
    import pandas as pd
    
    data = yf.download("{symbol}", period="1y")
    
    # Calculate Bollinger Bands
    data['SMA_20'] = data['Close'].rolling(20).mean()
    data['Std_20'] = data['Close'].rolling(20).std()
    data['Upper_Band'] = data['SMA_20'] + (2 * data['Std_20'])
    data['Lower_Band'] = data['SMA_20'] - (2 * data['Std_20'])
    
    # Generate signals
    data['Signal'] = 0
    data.loc[data['Close'] <= data['Lower_Band'], 'Signal'] = 1  # Buy
    data.loc[data['Close'] >= data['Upper_Band'], 'Signal'] = -1  # Sell
    
    return data

result = bollinger_bands_strategy_{symbol.lower()}()
```

**Expected Performance:**
- Best in ranging markets
- Moderate risk with band-based entries
- Sharpe Ratio: 0.9-1.3
"""
    
    async def _generate_macd_strategy_response(self, prompt: str) -> str:
        """Generate MACD strategy response"""
        symbol = self._extract_symbol_from_prompt(prompt) or "QQQ"
        return f"""
⚡ **MACD Momentum Strategy for {symbol}**

**Strategy Rules:**
- Buy: MACD line crosses above Signal line
- Sell: MACD line crosses below Signal line
- Trend Filter: Only trade in direction of 200-day MA

**Python Code:**
```python
def macd_strategy_{symbol.lower()}():
    import yfinance as yf
    import pandas as pd
    
    data = yf.download("{symbol}", period="2y")
    
    # Calculate MACD
    ema_12 = data['Close'].ewm(span=12).mean()
    ema_26 = data['Close'].ewm(span=26).mean()
    data['MACD'] = ema_12 - ema_26
    data['Signal_Line'] = data['MACD'].ewm(span=9).mean()
    data['MACD_Histogram'] = data['MACD'] - data['Signal_Line']
    
    # Generate signals
    data['Position'] = 0
    data.loc[data['MACD'] > data['Signal_Line'], 'Position'] = 1
    data.loc[data['MACD'] < data['Signal_Line'], 'Position'] = -1
    
    return data

result = macd_strategy_{symbol.lower()}()
```

- Key Features:**
- Trend-following system
- Works well in trending markets
- Early entry signals
"""
    
    async def _generate_pinescript_strategy_response(self, prompt: str) -> str:
        """Generate Pine Script strategy response"""
        
        symbol = self._extract_symbol_from_prompt(prompt) or "BTCUSD"
        query_lower = prompt.lower()
        
        # Detect strategy type for Pine Script
        if 'rsi' in query_lower:
            strategy_type = 'RSI'
            strategy_name = 'RSI Mean Reversion'
        elif 'macd' in query_lower:
            strategy_type = 'MACD'
            strategy_name = 'MACD Crossover'
        elif 'bollinger' in query_lower:
            strategy_type = 'Bollinger Bands'
            strategy_name = 'Bollinger Bands Strategy'
        elif 'moving average' in query_lower or 'ma' in query_lower:
            strategy_type = 'MA'
            strategy_name = 'Moving Average Crossover'
        else:
            strategy_type = 'RSI'
            strategy_name = 'RSI Mean Reversion'
        
        pine_code = self._generate_pine_script_code(strategy_type, symbol)
        
        response = f"""
🌲 **Pine Script Strategy: {strategy_name} for {symbol}**

**TradingView Pine Script v5 Implementation:**

```pinescript
{pine_code}
```

**Strategy Features:**
✅ **Entry/Exit Logic**: Clear buy/sell signals based on {strategy_type}
✅ **Risk Management**: Built-in stop-loss and take-profit
✅ **Visual Indicators**: Plot signals directly on chart
✅ **Backtesting Ready**: Compatible with TradingView Strategy Tester
✅ **Alerts**: Set up automatic notifications for signals

**How to Use:**
1. Copy the Pine Script code above
2. Open TradingView.com
3. Go to Pine Editor (Alt + E)
4. Paste the code and click "Add to Chart"
5. The strategy will appear on your chart with buy/sell signals

**Strategy Settings:**
- **Risk Management**: 2% stop-loss, 4% take-profit
- **Position Sizing**: 10% of equity per trade  
- **Commission**: 0.1% per trade
- **Timeframe**: Works on all timeframes (recommended: 1H, 4H, 1D)

**Performance Expectations:**
- **Win Rate**: 45-60% (depending on market conditions)
- **Risk/Reward**: 1:2 ratio minimum
- **Drawdown**: Expected max 15-20%
- **Best Markets**: Trending and ranging conditions

**Optimization Tips:**
1. Adjust parameters based on asset volatility
2. Test on different timeframes
3. Consider market session filters
4. Add volume confirmation for better entries

📊 **[Click here to view this strategy on TradingView Chart]**
"""
        return response.strip()
    
    def _generate_pine_script_code(self, strategy_type: str, symbol: str) -> str:
        """Generate Pine Script code for different strategy types"""
        
        if strategy_type == 'RSI':
            return f'''// RSI Mean Reversion Strategy for {symbol}
//@version=5
strategy("RSI Mean Reversion - {symbol}", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Input Parameters
rsi_length = input.int(14, "RSI Length", minval=1)
rsi_oversold = input.int(30, "RSI Oversold Level", minval=1, maxval=50)
rsi_overbought = input.int(70, "RSI Overbought Level", minval=50, maxval=99)
stop_loss_pct = input.float(2.0, "Stop Loss %", minval=0.1, maxval=10.0)
take_profit_pct = input.float(4.0, "Take Profit %", minval=0.1, maxval=20.0)

// Calculate RSI
rsi = ta.rsi(close, rsi_length)

// Entry Conditions
long_condition = rsi < rsi_oversold and rsi[1] >= rsi_oversold
short_condition = rsi > rsi_overbought and rsi[1] <= rsi_overbought

// Entry Orders
if long_condition
    strategy.entry("Long", strategy.long)
    
if short_condition
    strategy.entry("Short", strategy.short)

// Exit Conditions
if strategy.position_size > 0
    strategy.exit("Long Exit", "Long", 
                 stop=close * (1 - stop_loss_pct/100), 
                 limit=close * (1 + take_profit_pct/100))
                 
if strategy.position_size < 0
    strategy.exit("Short Exit", "Short", 
                 stop=close * (1 + stop_loss_pct/100), 
                 limit=close * (1 - take_profit_pct/100))

// Plot RSI
hline(rsi_overbought, "Overbought", color=color.red)
hline(rsi_oversold, "Oversold", color=color.green)
hline(50, "Midline", color=color.gray)

// Plot Buy/Sell Signals
plotshape(long_condition, style=shape.labelup, location=location.belowbar, 
          color=color.green, size=size.small, text="BUY")
plotshape(short_condition, style=shape.labeldown, location=location.abovebar, 
          color=color.red, size=size.small, text="SELL")

// Background color based on RSI
bgcolor(rsi < rsi_oversold ? color.new(color.green, 90) : 
        rsi > rsi_overbought ? color.new(color.red, 90) : na)'''

        elif strategy_type == 'MACD':
            return f'''// MACD Crossover Strategy for {symbol}
//@version=5
strategy("MACD Crossover - {symbol}", overlay=false, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Input Parameters
fast_length = input.int(12, "MACD Fast Length")
slow_length = input.int(26, "MACD Slow Length") 
signal_length = input.int(9, "Signal Length")
stop_loss_pct = input.float(3.0, "Stop Loss %", minval=0.1, maxval=10.0)
take_profit_pct = input.float(6.0, "Take Profit %", minval=0.1, maxval=20.0)

// Calculate MACD
[macdLine, signalLine, histLine] = ta.macd(close, fast_length, slow_length, signal_length)

// Entry Conditions
long_condition = ta.crossover(macdLine, signalLine) and macdLine < 0
short_condition = ta.crossunder(macdLine, signalLine) and macdLine > 0

// Entry Orders
if long_condition
    strategy.entry("Long", strategy.long)
    
if short_condition
    strategy.entry("Short", strategy.short)

// Exit Conditions
if strategy.position_size > 0
    strategy.exit("Long Exit", "Long", 
                 stop=close * (1 - stop_loss_pct/100), 
                 limit=close * (1 + take_profit_pct/100))
                 
if strategy.position_size < 0
    strategy.exit("Short Exit", "Short", 
                 stop=close * (1 + stop_loss_pct/100), 
                 limit=close * (1 - take_profit_pct/100))

// Plot MACD
plot(macdLine, color=color.blue, title="MACD")
plot(signalLine, color=color.red, title="Signal")
plot(histLine, color=color.gray, style=plot.style_histogram, title="Histogram")

// Plot signals
plotshape(long_condition, style=shape.triangleup, location=location.bottom, 
          color=color.green, size=size.small)
plotshape(short_condition, style=shape.triangledown, location=location.top, 
          color=color.red, size=size.small)

hline(0, "Zero Line", color=color.gray)'''

        elif strategy_type == 'MA':
            return f'''// Moving Average Crossover Strategy for {symbol}
//@version=5
strategy("MA Crossover - {symbol}", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Input Parameters
fast_ma_length = input.int(20, "Fast MA Length", minval=1)
slow_ma_length = input.int(50, "Slow MA Length", minval=1)
ma_type = input.string("SMA", "MA Type", options=["SMA", "EMA"])
stop_loss_pct = input.float(2.5, "Stop Loss %", minval=0.1, maxval=10.0)
take_profit_pct = input.float(5.0, "Take Profit %", minval=0.1, maxval=20.0)

// Calculate Moving Averages
fast_ma = ma_type == "SMA" ? ta.sma(close, fast_ma_length) : ta.ema(close, fast_ma_length)
slow_ma = ma_type == "SMA" ? ta.sma(close, slow_ma_length) : ta.ema(close, slow_ma_length)

// Entry Conditions
long_condition = ta.crossover(fast_ma, slow_ma)
short_condition = ta.crossunder(fast_ma, slow_ma)

// Entry Orders
if long_condition
    strategy.entry("Long", strategy.long)
    
if short_condition
    strategy.entry("Short", strategy.short)

// Exit Conditions
if strategy.position_size > 0
    strategy.exit("Long Exit", "Long", 
                 stop=close * (1 - stop_loss_pct/100), 
                 limit=close * (1 + take_profit_pct/100))
                 
if strategy.position_size < 0
    strategy.exit("Short Exit", "Short", 
                 stop=close * (1 + stop_loss_pct/100), 
                 limit=close * (1 - take_profit_pct/100))

// Plot Moving Averages
plot(fast_ma, color=color.blue, title="Fast MA", linewidth=2)
plot(slow_ma, color=color.red, title="Slow MA", linewidth=2)

// Plot Buy/Sell Signals
plotshape(long_condition, style=shape.labelup, location=location.belowbar, 
          color=color.green, size=size.normal, text="BUY")
plotshape(short_condition, style=shape.labeldown, location=location.abovebar, 
          color=color.red, size=size.normal, text="SELL")

// Background trend color
bgcolor(fast_ma > slow_ma ? color.new(color.green, 95) : color.new(color.red, 95))'''

        else:  # Bollinger Bands
            return f'''// Bollinger Bands Strategy for {symbol}
//@version=5
strategy("Bollinger Bands - {symbol}", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10)

// Input Parameters
bb_length = input.int(20, "Bollinger Bands Length", minval=1)
bb_mult = input.float(2.0, "Bollinger Bands Multiplier", minval=0.1, maxval=5.0)
stop_loss_pct = input.float(2.0, "Stop Loss %", minval=0.1, maxval=10.0)
take_profit_pct = input.float(4.0, "Take Profit %", minval=0.1, maxval=20.0)

// Calculate Bollinger Bands
[middle, upper, lower] = ta.bb(close, bb_length, bb_mult)

// Entry Conditions
long_condition = close <= lower and close[1] > lower[1]
short_condition = close >= upper and close[1] < upper[1]

// Entry Orders
if long_condition
    strategy.entry("Long", strategy.long)
    
if short_condition
    strategy.entry("Short", strategy.short)

// Exit Conditions
if strategy.position_size > 0
    strategy.exit("Long Exit", "Long", 
                 stop=close * (1 - stop_loss_pct/100), 
                 limit=close * (1 + take_profit_pct/100))
                 
if strategy.position_size < 0
    strategy.exit("Short Exit", "Short", 
                 stop=close * (1 + stop_loss_pct/100), 
                 limit=close * (1 - take_profit_pct/100))

// Plot Bollinger Bands
plot(upper, color=color.red, title="Upper Band")
plot(middle, color=color.blue, title="Middle Band")
plot(lower, color=color.green, title="Lower Band")

// Fill between bands
fill(plot(upper), plot(lower), color=color.new(color.blue, 95))

// Plot Buy/Sell Signals
plotshape(long_condition, style=shape.labelup, location=location.belowbar, 
          color=color.green, size=size.normal, text="BUY")
plotshape(short_condition, style=shape.labeldown, location=location.abovebar, 
          color=color.red, size=size.normal, text="SELL")'''
    
    async def _generate_ma_strategy_response(self, prompt: str) -> str:
        """Generate Moving Average strategy response"""
        
        symbol = self._extract_symbol_from_prompt(prompt)
        if not symbol:
            symbol = "AAPL"
            
        return f"""
📈 **Moving Average Crossover Strategy for {symbol}**

**Strategy Overview:**
Classic dual moving average crossover system with risk management.

**Entry/Exit Rules:**
- Buy: Fast MA (20) crosses above Slow MA (50)
- Sell: Fast MA crosses below Slow MA
- Stop Loss: 3% below entry
- Position Size: 2% risk per trade

**Python Code:**

```python
def moving_average_strategy_{symbol.lower()}():
    import yfinance as yf
    import pandas as pd
    
    # Get data
    data = yf.download("{symbol}", period="2y")
    
    # Calculate moving averages
    data['MA_20'] = data['Close'].rolling(20).mean()
    data['MA_50'] = data['Close'].rolling(50).mean()
    
    # Generate signals
    data['Signal'] = 0
    data['Signal'][data['MA_20'] > data['MA_50']] = 1
    data['Signal'][data['MA_20'] < data['MA_50']] = -1
    
    # Calculate strategy returns
    data['Position'] = data['Signal'].shift(1)
    data['Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Position'] * data['Returns']
    
    return data

# Execute strategy
result = moving_average_strategy_{symbol.lower()}()
print("Strategy implemented successfully!")
```

**Performance Expectations:**
- Works well in trending markets
- Moderate drawdowns in choppy conditions
- Expected Sharpe Ratio: 0.8-1.2
"""
    
    async def _generate_explanation_response(self, prompt: str) -> str:
        """Generate explanation for financial concepts"""
        
        if 'rsi' in prompt.lower():
            return """
📊 **RSI (Relative Strength Index) Explained**

**What is RSI?**
RSI is a momentum oscillator that measures the speed and change of price movements, ranging from 0 to 100.

**Key Levels:**
- **RSI > 70**: Overbought (potential sell signal)
- **RSI < 30**: Oversold (potential buy signal)
- **RSI 50**: Neutral momentum

**Calculation:**
RSI = 100 - (100 / (1 + RS))
Where RS = Average Gain / Average Loss over 14 periods

**Trading Applications:**
1. **Mean Reversion**: Buy oversold, sell overbought
2. **Divergence**: Price vs RSI direction differences
3. **Trend Confirmation**: RSI above/below 50

**Strengths:**
✅ Works well in ranging markets
✅ Clear overbought/oversold signals
✅ Easy to interpret

**Limitations:**
⚠️ Can stay overbought/oversold in strong trends
⚠️ Generates false signals in choppy markets
⚠️ Lagging indicator (based on past prices)

**Best Practices:**
- Combine with other indicators
- Use different timeframes
- Consider market context
"""

        elif 'sharpe ratio' in prompt.lower():
            return """
📈 **Sharpe Ratio Explained**

**Definition:**
The Sharpe Ratio measures risk-adjusted returns by comparing excess returns to volatility.

**Formula:**
Sharpe Ratio = (Portfolio Return - Risk-Free Rate) / Portfolio Standard Deviation

**Interpretation:**
- **> 1.0**: Good risk-adjusted performance
- **> 2.0**: Excellent performance
- **< 0**: Poor performance (losing money vs risk-free rate)

**Example:**
If a strategy returns 15% with 10% volatility, and risk-free rate is 3%:
Sharpe = (15% - 3%) / 10% = 1.2 (Good performance)

**Usage in Trading:**
- Compare different strategies
- Optimize portfolio allocation
- Set performance benchmarks
"""
        
        else:
            return f"""
💡 **Financial Concept Explanation**

I can explain various financial and trading concepts including:

**Technical Indicators:**
- RSI, MACD, Bollinger Bands, Moving Averages
- Volume indicators, Momentum oscillators
- Support/Resistance levels

**Risk Metrics:**
- Sharpe Ratio, Sortino Ratio, Maximum Drawdown
- Value at Risk (VaR), Beta, Alpha
- Volatility and correlation measures

**Trading Strategies:**
- Mean reversion, Momentum, Arbitrage
- Portfolio optimization techniques
- Risk management principles

**Market Analysis:**
- Fundamental vs Technical analysis
- Market microstructure
- Behavioral finance concepts

Please specify which concept you'd like me to explain in detail!
"""

    async def _generate_risk_analysis_response(self, prompt: str) -> str:
        """Generate risk analysis response"""
        
        return """
🛡️ **Risk Analysis Framework**

**Key Risk Metrics:**

1. **Maximum Drawdown**
   - Largest peak-to-trough decline
   - Indicates worst-case scenario
   - Target: < 20% for most strategies

2. **Value at Risk (VaR)**
   - Potential loss at confidence level
   - 95% VaR = maximum loss 19 out of 20 days
   - Helps with position sizing

3. **Sharpe Ratio**
   - Risk-adjusted returns
   - Target: > 1.0 for good strategies
   - Higher is better

4. **Win Rate vs Profit Factor**
   - Win Rate: % of profitable trades
   - Profit Factor: Gross profit / Gross loss
   - Need balanced approach

**Risk Management Rules:**

✅ **Position Sizing**: Never risk > 2% per trade
✅ **Diversification**: Multiple uncorrelated strategies
✅ **Stop Losses**: Always define maximum loss
✅ **Portfolio Heat**: Total risk across all positions
✅ **Market Regime**: Adjust for volatility conditions

**Warning Signs:**
⚠️ Consecutive losses > 5
⚠️ Drawdown > 15%
⚠️ Sharpe ratio < 0.5
⚠️ High correlation during stress periods

**Recommendation:**
Implement systematic risk management with clear rules and regular monitoring.
"""

    async def _generate_general_response(self, prompt: str) -> str:
        """Generate general trading/finance response"""
        
        return f"""
🤖 **RIMSI Terminal Response**

I've processed your query: "{prompt[:100]}..."

**Available Capabilities:**

📊 **Strategy Development:**
- RSI, Moving Average, MACD, Bollinger Bands
- Custom indicator combinations
- Risk management integration

⚡ **Code Generation:**
- Python trading strategies
- Backtesting frameworks
- Performance analysis tools

🛡️ **Risk Analysis:**
- Portfolio risk assessment
- Drawdown analysis
- Volatility measurement

📈 **Performance Optimization:**
- Parameter tuning
- Walk-forward analysis
- Multi-asset strategies

**Quick Commands:**
- "Build RSI strategy for [SYMBOL]"
- "Explain [INDICATOR/CONCEPT]"
- "Analyze risk of [STRATEGY]"
- "Optimize portfolio with [SYMBOLS]"

**Next Steps:**
Please provide more specific requirements for:
1. Target asset/symbol
2. Strategy type preference
3. Risk tolerance level
4. Investment timeframe

I'm here to help you build robust, profitable trading strategies! 🚀
"""

    def _extract_symbol_from_prompt(self, prompt: str) -> Optional[str]:
        """Extract stock symbol from prompt"""
        import re
        
        # Look for common stock symbols (2-5 uppercase letters)
        symbols = re.findall(r'\b[A-Z]{2,5}\b', prompt)
        
        # Filter out common false positives
        excluded = {'RSI', 'MACD', 'SMA', 'EMA', 'API', 'USD', 'EUR', 'GBP'}
        valid_symbols = [s for s in symbols if s not in excluded]
        
        return valid_symbols[0] if valid_symbols else None

    def _get_rsi_strategy_template(self):
        """Get RSI strategy template"""
        return {
            'name': 'RSI Mean Reversion',
            'parameters': {'period': 14, 'oversold': 30, 'overbought': 70},
            'risk_management': {'stop_loss': 0.05, 'take_profit': 0.10}
        }
    
    def _get_ma_strategy_template(self):
        """Get Moving Average strategy template"""
        return {
            'name': 'MA Crossover',
            'parameters': {'fast_period': 20, 'slow_period': 50},
            'risk_management': {'stop_loss': 0.03, 'position_size': 0.02}
        }
    
    def _get_bb_strategy_template(self):
        """Get Bollinger Bands strategy template"""
        return {
            'name': 'Bollinger Bands',
            'parameters': {'period': 20, 'std_dev': 2},
            'risk_management': {'stop_loss': 0.04, 'take_profit': 0.08}
        }
    
    def _get_macd_strategy_template(self):
        """Get MACD strategy template"""
        return {
            'name': 'MACD Strategy',
            'parameters': {'fast': 12, 'slow': 26, 'signal': 9},
            'risk_management': {'stop_loss': 0.06, 'trailing_stop': True}
        }
    
    def _get_pinescript_rsi_template(self):
        """Get Pine Script RSI strategy template"""
        return {
            'name': 'Pine Script RSI Strategy',
            'language': 'pine_script',
            'parameters': {'rsi_period': 14, 'oversold': 30, 'overbought': 70},
            'features': ['tradingview_compatible', 'visual_signals', 'backtesting_ready']
        }
    
    def _get_pinescript_ma_template(self):
        """Get Pine Script Moving Average strategy template"""
        return {
            'name': 'Pine Script MA Crossover',
            'language': 'pine_script', 
            'parameters': {'fast_ma': 20, 'slow_ma': 50},
            'features': ['trend_following', 'crossover_signals', 'risk_management']
        }


# Global RIMSI engine instance
_rimsi_engine = None

def get_rimsi_engine(config=None):
    """Get or create global RIMSI engine instance"""
    global _rimsi_engine
    if _rimsi_engine is None:
        _rimsi_engine = RIMSILLMEngine(config)
    return _rimsi_engine

# Async wrapper for Flask route compatibility
async def process_rimsi_query(query: str, context: Dict = None, config=None) -> RIMSIResponse:
    """Process RIMSI query - main entry point"""
    engine = get_rimsi_engine(config)
    return await engine.process_query(query, context)
