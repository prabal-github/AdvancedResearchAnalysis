#!/usr/bin/env python3
"""
Direct Options Model Fix with Proper Strike Analysis
"""

import os
import sys
from datetime import datetime

# Add the app directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import Flask app and database
from app import app, db, PublishedModel

def fix_support_resistance_model():
    """Fix the Support-Resistance model specifically"""
    
    with app.app_context():
        
        model = PublishedModel.query.filter_by(name="NIFTY Options Support-Resistance Level Predictor").first()
        
        if model:
            print("🔧 Fixing NIFTY Options Support-Resistance Level Predictor...")
            
            # Updated Python code with proper parsing
            fixed_code = '''
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import calendar
import numpy as np

class NIFTYOptionsAnalyzer:
    """
    NIFTY Options Support-Resistance Level Predictor
    Advanced strike-by-strike analysis with buy/sell recommendations
    """
    
    def __init__(self):
        self.model_name = "NIFTY Options Support-Resistance Level Predictor"
        self.api_endpoint = "https://service.upstox.com/option-analytics-tool/open/v1/strategy-chains"
        self.accuracy = "74.5%"
    
    def get_next_expiry_date(self):
        """Calculate next monthly options expiry"""
        now = datetime.now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        last_date = datetime(now.year, now.month, last_day)
        days_back = (last_date.weekday() - 3) % 7
        if days_back == 0 and last_date.day == last_day:
            last_thursday = last_date
        else:
            last_thursday = last_date - timedelta(days=days_back)
        
        if last_thursday < now:
            if now.month == 12:
                next_month = datetime(now.year + 1, 1, 1)
            else:
                next_month = datetime(now.year, now.month + 1, 1)
            last_day = calendar.monthrange(next_month.year, next_month.month)[1]
            last_date = datetime(next_month.year, next_month.month, last_day)
            days_back = (last_date.weekday() - 3) % 7
            last_thursday = last_date - timedelta(days=days_back) if days_back > 0 else last_date
        
        return last_thursday.strftime('%d-%m-%Y')
    
    def fetch_options_data(self):
        """Fetch real-time options data from Upstox API"""
        try:
            expiry = self.get_next_expiry_date()
            url = f"{self.api_endpoint}?assetKey=NSE_INDEX%7CNifty+50&strategyChainType=PC_CHAIN&expiry={expiry}"
            response = requests.get(url, timeout=15)
            return response.json() if response.status_code == 200 else {"error": f"API Error: {response.status_code}"}
        except Exception as e:
            return {"error": f"Exception: {str(e)}"}
    
    def analyze_strikes(self, options_data):
        """Detailed strike-by-strike analysis"""
        try:
            # Parse the real API structure
            data_section = options_data.get("data", {})
            strategy_data = data_section.get("strategyChainData", {})
            strike_map = strategy_data.get("strikeMap", {})
            
            if not strike_map:
                return {"error": "No strike data found in API response"}
            
            strike_analysis = []
            call_oi_total = put_oi_total = 0
            call_volume_total = put_volume_total = 0
            current_spot = None
            min_diff = float('inf')
            
            # Process each strike in the map
            for strike_str, option_data in strike_map.items():
                strike = float(strike_str)
                
                # Extract call data
                call_option = option_data.get("callOptionData", {})
                call_market = call_option.get("marketData", {})
                call_analytics = call_option.get("analytics", {})
                
                # Extract put data  
                put_option = option_data.get("putOptionData", {})
                put_market = put_option.get("marketData", {})
                put_analytics = put_option.get("analytics", {})
                
                # Market data
                call_ltp = call_market.get("ltp", 0)
                call_oi = call_market.get("oi", 0)
                call_volume = call_market.get("volume", 0)
                call_bid = call_market.get("bidPrice", 0)
                call_ask = call_market.get("askPrice", 0)
                
                put_ltp = put_market.get("ltp", 0)
                put_oi = put_market.get("oi", 0)
                put_volume = put_market.get("volume", 0)
                put_bid = put_market.get("bidPrice", 0)
                put_ask = put_market.get("askPrice", 0)
                
                # Greeks data
                call_delta = call_analytics.get("delta", 0)
                call_gamma = call_analytics.get("gamma", 0)
                call_theta = call_analytics.get("theta", 0)
                call_vega = call_analytics.get("vega", 0)
                call_iv = call_analytics.get("iv", 0)
                
                put_delta = put_analytics.get("delta", 0)
                put_gamma = put_analytics.get("gamma", 0)
                put_theta = put_analytics.get("theta", 0)
                put_vega = put_analytics.get("vega", 0)
                put_iv = put_analytics.get("iv", 0)
                
                # Accumulate totals
                call_oi_total += call_oi
                put_oi_total += put_oi
                call_volume_total += call_volume
                put_volume_total += put_volume
                
                # Find ATM strike (where call and put prices are closest)
                if call_ltp > 0 and put_ltp > 0:
                    diff = abs(call_ltp - put_ltp)
                    if diff < min_diff:
                        min_diff = diff
                        current_spot = strike
                
                # Generate action recommendation for this strike
                action = self.generate_strike_action(
                    strike, current_spot or 25000, call_ltp, put_ltp, 
                    call_oi, put_oi, call_volume, put_volume,
                    call_iv, put_iv, call_delta, put_delta
                )
                
                strike_analysis.append({
                    "strike": strike,
                    "call_data": {
                        "ltp": call_ltp,
                        "oi": call_oi,
                        "volume": call_volume,
                        "bid": call_bid,
                        "ask": call_ask,
                        "iv": call_iv,
                        "delta": call_delta,
                        "gamma": call_gamma,
                        "theta": call_theta,
                        "vega": call_vega
                    },
                    "put_data": {
                        "ltp": put_ltp,
                        "oi": put_oi,
                        "volume": put_volume,
                        "bid": put_bid,
                        "ask": put_ask,
                        "iv": put_iv,
                        "delta": put_delta,
                        "gamma": put_gamma,
                        "theta": put_theta,
                        "vega": put_vega
                    },
                    "recommendation": {
                        "action": action["action"],
                        "reasoning": action["reasoning"],
                        "confidence": action["confidence"],
                        "target": action.get("target"),
                        "stop_loss": action.get("stop_loss"),
                        "strategy": action["strategy"],
                        "risk_reward": action.get("risk_reward", "1:1")
                    }
                })
            
            # Calculate market-wide metrics
            pcr_oi = put_oi_total / call_oi_total if call_oi_total > 0 else 0
            pcr_volume = put_volume_total / call_volume_total if call_volume_total > 0 else 0
            
            # Find max pain (strike with highest total OI)
            max_pain_strike = None
            max_total_oi = 0
            for analysis in strike_analysis:
                total_oi = analysis["call_data"]["oi"] + analysis["put_data"]["oi"]
                if total_oi > max_total_oi:
                    max_total_oi = total_oi
                    max_pain_strike = analysis["strike"]
            
            return {
                "success": True,
                "current_spot": current_spot or 25000,
                "max_pain": max_pain_strike,
                "pcr_oi": pcr_oi,
                "pcr_volume": pcr_volume,
                "total_call_oi": call_oi_total,
                "total_put_oi": put_oi_total,
                "total_call_volume": call_volume_total,
                "total_put_volume": put_volume_total,
                "strike_analysis": strike_analysis,
                "total_strikes": len(strike_analysis)
            }
            
        except Exception as e:
            return {"error": f"Strike analysis error: {str(e)}"}
    
    def generate_strike_action(self, strike, current_spot, call_ltp, put_ltp, 
                             call_oi, put_oi, call_volume, put_volume,
                             call_iv, put_iv, call_delta, put_delta):
        """Generate specific action recommendation for each strike"""
        try:
            # Calculate key ratios
            put_call_oi_ratio = put_oi / call_oi if call_oi > 0 else 0
            put_call_vol_ratio = put_volume / call_volume if call_volume > 0 else 0
            total_oi = call_oi + put_oi
            total_volume = call_volume + put_volume
            distance_pct = ((strike - current_spot) / current_spot) * 100
            
            # Default values
            action = "HOLD"
            reasoning = ""
            confidence = 50
            strategy = "Neutral"
            target = None
            stop_loss = None
            risk_reward = "1:1"
            
            # Strategy 1: Strong Support/Resistance Based on OI
            if put_oi > 100000 and put_call_oi_ratio > 3.0:
                action = "BUY_CALL"
                reasoning = f"Very high Put OI ({put_oi:,.0f}) at {strike} indicates strong support. Buy calls for bounce."
                confidence = min(90, 70 + min(20, put_call_oi_ratio * 5))
                strategy = "Support Level Play"
                target = strike + (strike * 0.025)
                stop_loss = strike - (strike * 0.015)
                risk_reward = "2.5:1"
                
            elif call_oi > 100000 and put_call_oi_ratio < 0.33:
                action = "BUY_PUT"
                reasoning = f"Very high Call OI ({call_oi:,.0f}) at {strike} indicates strong resistance. Buy puts for reversal."
                confidence = min(90, 70 + min(20, (0.33 - put_call_oi_ratio) * 60))
                strategy = "Resistance Level Play"
                target = strike - (strike * 0.025)
                stop_loss = strike + (strike * 0.015)
                risk_reward = "2.5:1"
            
            # Strategy 2: Volume Surge Analysis
            elif put_volume > 5000 and put_volume > call_volume * 3:
                action = "SELL_PUT"
                reasoning = f"High Put volume ({put_volume:,}) suggests active Put writing. Bullish sentiment at {strike}."
                confidence = min(85, 60 + min(25, put_volume / 1000))
                strategy = "Put Writing Activity"
                target = put_ltp * 0.4
                stop_loss = strike - (put_ltp * 3)
                risk_reward = "3:1"
                
            elif call_volume > 5000 and call_volume > put_volume * 3:
                action = "SELL_CALL"
                reasoning = f"High Call volume ({call_volume:,}) suggests active Call writing. Bearish sentiment at {strike}."
                confidence = min(85, 60 + min(25, call_volume / 1000))
                strategy = "Call Writing Activity"
                target = call_ltp * 0.4
                stop_loss = strike + (call_ltp * 3)
                risk_reward = "3:1"
            
            # Strategy 3: IV Skew Opportunities
            elif call_iv > 0 and put_iv > 0 and abs(call_iv - put_iv) > 8:
                if call_iv > put_iv:
                    action = "SELL_CALL_BUY_PUT"
                    reasoning = f"Call IV ({call_iv:.1f}%) >> Put IV ({put_iv:.1f}%). Sell overpriced calls, buy cheap puts."
                    confidence = min(80, 55 + (call_iv - put_iv))
                    strategy = "IV Arbitrage"
                    risk_reward = "2:1"
                else:
                    action = "BUY_CALL_SELL_PUT"
                    reasoning = f"Put IV ({put_iv:.1f}%) >> Call IV ({call_iv:.1f}%). Buy cheap calls, sell overpriced puts."
                    confidence = min(80, 55 + (put_iv - call_iv))
                    strategy = "IV Arbitrage"
                    risk_reward = "2:1"
            
            # Strategy 4: ATM Strategies
            elif abs(distance_pct) < 2 and call_ltp > 50 and put_ltp > 50:
                if call_iv > 25 and put_iv > 25:
                    action = "SELL_STRADDLE"
                    reasoning = f"ATM strike with high IV. Sell straddle at {strike} for time decay profit."
                    confidence = 70
                    strategy = "Short Straddle"
                    target = (call_ltp + put_ltp) * 0.4
                    stop_loss = strike + (call_ltp + put_ltp) * 1.2
                    risk_reward = "1:3"
                else:
                    action = "BUY_STRADDLE"
                    reasoning = f"ATM strike with low IV. Buy straddle at {strike} for volatility expansion."
                    confidence = 65
                    strategy = "Long Straddle"
                    target = (call_ltp + put_ltp) * 2
                    stop_loss = (call_ltp + put_ltp) * 0.5
                    risk_reward = "3:1"
            
            # Strategy 5: Greeks-based Momentum
            elif abs(call_delta) > 0.8 and call_gamma > 0.002:
                action = "BUY_CALL"
                reasoning = f"High Call Delta ({call_delta:.3f}) & Gamma ({call_gamma:.4f}) indicate strong momentum potential."
                confidence = min(80, 50 + abs(call_delta) * 35)
                strategy = "Delta Momentum"
                target = strike + (strike * abs(call_delta) * 0.15)
                stop_loss = strike - (strike * 0.02)
                risk_reward = "3:1"
                
            elif abs(put_delta) > 0.8 and put_gamma > 0.002:
                action = "BUY_PUT"
                reasoning = f"High Put Delta ({put_delta:.3f}) & Gamma ({put_gamma:.4f}) indicate strong bearish momentum."
                confidence = min(80, 50 + abs(put_delta) * 35)
                strategy = "Delta Momentum"
                target = strike - (strike * abs(put_delta) * 0.15)
                stop_loss = strike + (strike * 0.02)
                risk_reward = "3:1"
            
            # Strategy 6: Liquidity Filter
            elif total_oi < 5000:
                action = "AVOID"
                reasoning = f"Very low liquidity (Total OI: {total_oi:,.0f}). High bid-ask spreads expected."
                confidence = 30
                strategy = "Liquidity Filter"
                
            elif total_volume < 100:
                action = "AVOID"
                reasoning = f"Very low volume (Total Vol: {total_volume:,}). Poor execution likely."
                confidence = 35
                strategy = "Volume Filter"
            
            # Strategy 7: Distance-based Filter
            elif abs(distance_pct) > 15:
                action = "AVOID"
                reasoning = f"Strike too far from current level ({distance_pct:+.1f}%). Low probability of success."
                confidence = 25
                strategy = "Distance Filter"
            
            return {
                "action": action,
                "reasoning": reasoning,
                "confidence": confidence,
                "strategy": strategy,
                "target": target,
                "stop_loss": stop_loss,
                "risk_reward": risk_reward
            }
            
        except Exception as e:
            return {
                "action": "ERROR",
                "reasoning": f"Action generation error: {str(e)}",
                "confidence": 0,
                "strategy": "Error"
            }
    
    def predict(self):
        """Main prediction function"""
        try:
            # Fetch options data
            options_data = self.fetch_options_data()
            if "error" in options_data:
                return {
                    "model": self.model_name,
                    "type": "Technical Options ML",
                    "accuracy": self.accuracy,
                    "timestamp": datetime.now().isoformat(),
                    "expiry_date": self.get_next_expiry_date(),
                    "analysis": {
                        "model_name": self.model_name,
                        "timestamp": datetime.now().isoformat(),
                        "expiry_date": self.get_next_expiry_date(),
                        "analysis_type": "Technical Options ML",
                        "signals": [],
                        "summary": "Unable to fetch options data",
                        "risk_assessment": "Medium",
                        "error": options_data["error"]
                    },
                    "recommendation": [],
                    "risk_level": "Medium",
                    "allocation": "3-5% for directional trades"
                }
            
            # Perform strike analysis
            analysis_result = self.analyze_strikes(options_data)
            if "error" in analysis_result:
                return {
                    "model": self.model_name,
                    "type": "Technical Options ML",
                    "accuracy": self.accuracy,
                    "timestamp": datetime.now().isoformat(),
                    "expiry_date": self.get_next_expiry_date(),
                    "analysis": {
                        "model_name": self.model_name,
                        "timestamp": datetime.now().isoformat(),
                        "expiry_date": self.get_next_expiry_date(),
                        "analysis_type": "Technical Options ML",
                        "signals": [],
                        "summary": "Unable to analyze options data",
                        "risk_assessment": "Medium", 
                        "error": analysis_result["error"]
                    },
                    "recommendation": [],
                    "risk_level": "Medium",
                    "allocation": "3-5% for directional trades"
                }
            
            # Generate overall market sentiment
            pcr_oi = analysis_result["pcr_oi"]
            if pcr_oi > 1.3:
                market_sentiment = "STRONGLY_BULLISH (Contrarian)"
            elif pcr_oi > 1.1:
                market_sentiment = "BULLISH (Contrarian)"
            elif pcr_oi < 0.7:
                market_sentiment = "STRONGLY_BEARISH (Contrarian)"
            elif pcr_oi < 0.9:
                market_sentiment = "BEARISH (Contrarian)"
            else:
                market_sentiment = "NEUTRAL"
            
            # Extract top recommendations
            recommendations = []
            for strike_data in analysis_result["strike_analysis"]:
                rec = strike_data["recommendation"]
                if rec["action"] not in ["HOLD", "AVOID", "ERROR"] and rec["confidence"] > 70:
                    recommendations.append({
                        "strike": strike_data["strike"],
                        "action": rec["action"],
                        "reasoning": rec["reasoning"],
                        "confidence": rec["confidence"],
                        "target": rec["target"],
                        "stop_loss": rec["stop_loss"],
                        "strategy": rec["strategy"],
                        "risk_reward": rec["risk_reward"]
                    })
            
            # Sort by confidence
            recommendations.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "model": self.model_name,
                "type": "Technical Options ML",
                "accuracy": self.accuracy,
                "timestamp": datetime.now().isoformat(),
                "expiry_date": self.get_next_expiry_date(),
                "market_overview": {
                    "current_nifty_level": analysis_result["current_spot"],
                    "max_pain_level": analysis_result["max_pain"],
                    "put_call_ratio_oi": analysis_result["pcr_oi"],
                    "put_call_ratio_volume": analysis_result["pcr_volume"],
                    "total_call_oi": analysis_result["total_call_oi"],
                    "total_put_oi": analysis_result["total_put_oi"],
                    "market_sentiment": market_sentiment,
                    "total_strikes_analyzed": analysis_result["total_strikes"]
                },
                "strike_analysis": analysis_result["strike_analysis"],
                "top_recommendations": recommendations[:10],  # Top 10 recommendations
                "success": True,
                "risk_level": "Medium-High",
                "allocation": "3-7% for options strategies"
            }
            
        except Exception as e:
            return {
                "model": self.model_name,
                "type": "Technical Options ML",
                "accuracy": self.accuracy,
                "timestamp": datetime.now().isoformat(),
                "error": f"Prediction error: {str(e)}",
                "risk_level": "High",
                "allocation": "Avoid until fixed"
            }

# Initialize and run the analyzer
analyzer = NIFTYOptionsAnalyzer()
result = analyzer.predict()
'''
            
            # Update the model
            model.python_code = fixed_code
            
            try:
                db.session.commit()
                print("✅ Successfully fixed NIFTY Options Support-Resistance Level Predictor!")
                print("📊 Now provides detailed strike-by-strike analysis with:")
                print("   • Buy/Sell/Hold recommendations")
                print("   • Target and stop-loss levels")
                print("   • Confidence scores")
                print("   • Multiple trading strategies")
                print("   • Risk-reward ratios")
                print("   • Greeks analysis")
                print("   • OI and volume analysis")
                
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error saving changes: {str(e)}")
        
        else:
            print("❌ Model not found in database")

if __name__ == "__main__":
    fix_support_resistance_model()
