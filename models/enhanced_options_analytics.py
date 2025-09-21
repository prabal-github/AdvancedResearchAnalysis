"""
Enhanced Options Analytics - Additional Features for Options Analyzer
Advanced analytics to supplement the existing options analyzer
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import norm, skew, kurtosis
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class EnhancedOptionsAnalytics:
    def __init__(self):
        self.name = "Enhanced Options Analytics"
        self.version = "1.0.0"
    
    def calculate_advanced_greeks(self, options_data, spot_price, risk_free_rate=0.05):
        """Calculate advanced Greeks and risk metrics"""
        try:
            enhanced_metrics = {}
            
            # Portfolio-level Greeks
            portfolio_delta = sum(row.get('call_delta', 0) * row.get('call_oi', 0) + 
                                 row.get('put_delta', 0) * row.get('put_oi', 0) 
                                 for row in options_data)
            
            portfolio_gamma = sum(row.get('call_gamma', 0) * row.get('call_oi', 0) + 
                                 row.get('put_gamma', 0) * row.get('put_oi', 0) 
                                 for row in options_data)
            
            # Gamma exposure calculation
            gamma_exposure = {}
            for row in options_data:
                strike = row['strike']
                call_gamma_exposure = row.get('call_gamma', 0) * row.get('call_oi', 0) * spot_price * spot_price / 100
                put_gamma_exposure = row.get('put_gamma', 0) * row.get('put_oi', 0) * spot_price * spot_price / 100
                gamma_exposure[strike] = call_gamma_exposure + put_gamma_exposure
            
            # Dark pools and gamma walls
            max_gamma_strike = max(gamma_exposure.keys(), key=lambda k: gamma_exposure[k])
            
            enhanced_metrics.update({
                'portfolio_delta': portfolio_delta,
                'portfolio_gamma': portfolio_gamma, 
                'gamma_exposure_by_strike': gamma_exposure,
                'max_gamma_strike': max_gamma_strike,
                'gamma_wall_strength': gamma_exposure[max_gamma_strike]
            })
            
            return enhanced_metrics
            
        except Exception as e:
            logger.error(f"Error calculating advanced Greeks: {e}")
            return {}
    
    def calculate_volatility_analytics(self, options_data):
        """Advanced volatility surface analysis"""
        try:
            call_ivs = [row.get('call_iv', 0) for row in options_data if row.get('call_iv', 0) > 0]
            put_ivs = [row.get('put_iv', 0) for row in options_data if row.get('put_iv', 0) > 0]
            
            if not call_ivs or not put_ivs:
                return {}
            
            # Volatility skew analysis
            strikes = [row['strike'] for row in options_data]
            call_iv_skew = np.polyfit(strikes, call_ivs, 2) if len(call_ivs) > 2 else [0, 0, 0]
            put_iv_skew = np.polyfit(strikes, put_ivs, 2) if len(put_ivs) > 2 else [0, 0, 0]
            
            # Term structure analysis (simplified)
            volatility_analytics = {
                'call_iv_mean': np.mean(call_ivs),
                'call_iv_std': np.std(call_ivs),
                'put_iv_mean': np.mean(put_ivs),
                'put_iv_std': np.std(put_ivs),
                'iv_spread': np.mean(call_ivs) - np.mean(put_ivs),
                'call_iv_skew_coefficient': call_iv_skew[0],
                'put_iv_skew_coefficient': put_iv_skew[0],
                'volatility_smile_asymmetry': skew(call_ivs),
                'volatility_smile_kurtosis': kurtosis(call_ivs),
                'iv_percentile_rank': self._calculate_iv_percentile(call_ivs)
            }
            
            return volatility_analytics
            
        except Exception as e:
            logger.error(f"Error calculating volatility analytics: {e}")
            return {}
    
    def analyze_flow_patterns(self, options_data):
        """Analyze options flow patterns and sentiment"""
        try:
            call_volume = sum(row.get('call_volume', 0) for row in options_data)
            put_volume = sum(row.get('put_volume', 0) for row in options_data)
            
            call_oi = sum(row.get('call_oi', 0) for row in options_data)
            put_oi = sum(row.get('put_oi', 0) for row in options_data)
            
            # Flow analysis
            flow_analytics = {
                'total_call_volume': call_volume,
                'total_put_volume': put_volume,
                'volume_pcr': put_volume / max(call_volume, 1),
                'oi_pcr': put_oi / max(call_oi, 1),
                'volume_oi_ratio_calls': call_volume / max(call_oi, 1),
                'volume_oi_ratio_puts': put_volume / max(put_oi, 1)
            }
            
            # Unusual activity detection
            unusual_activity = []
            for row in options_data:
                call_vol_oi_ratio = row.get('call_volume', 0) / max(row.get('call_oi', 1), 1)
                put_vol_oi_ratio = row.get('put_volume', 0) / max(row.get('put_oi', 1), 1)
                
                if call_vol_oi_ratio > 2.0:  # High call activity
                    unusual_activity.append({
                        'strike': row['strike'],
                        'type': 'call',
                        'activity_ratio': call_vol_oi_ratio,
                        'volume': row.get('call_volume', 0)
                    })
                
                if put_vol_oi_ratio > 2.0:  # High put activity
                    unusual_activity.append({
                        'strike': row['strike'],
                        'type': 'put',
                        'activity_ratio': put_vol_oi_ratio,
                        'volume': row.get('put_volume', 0)
                    })
            
            flow_analytics['unusual_activity'] = unusual_activity
            flow_analytics['sentiment_score'] = self._calculate_sentiment_score(flow_analytics)
            
            return flow_analytics
            
        except Exception as e:
            logger.error(f"Error analyzing flow patterns: {e}")
            return {}
    
    def calculate_support_resistance_levels(self, options_data, spot_price):
        """Calculate support and resistance levels from options data"""
        try:
            # Weighted by open interest
            levels = []
            
            for row in options_data:
                strike = row['strike']
                total_oi = row.get('call_oi', 0) + row.get('put_oi', 0)
                
                if total_oi > 0:
                    # Gamma exposure calculation for strike significance
                    gamma_weight = (row.get('call_gamma', 0) + row.get('put_gamma', 0)) * total_oi
                    levels.append({
                        'strike': strike,
                        'oi_weight': total_oi,
                        'gamma_weight': gamma_weight,
                        'distance_from_spot': abs(strike - spot_price) / spot_price * 100
                    })
            
            # Sort by significance (OI + Gamma weight)
            levels.sort(key=lambda x: x['oi_weight'] + x['gamma_weight'], reverse=True)
            
            # Identify key levels
            resistance_levels = [l for l in levels if l['strike'] > spot_price][:3]
            support_levels = [l for l in levels if l['strike'] < spot_price][:3]
            
            return {
                'resistance_levels': resistance_levels,
                'support_levels': support_levels,
                'key_level_analysis': {
                    'strongest_resistance': resistance_levels[0] if resistance_levels else None,
                    'strongest_support': support_levels[0] if support_levels else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {}
    
    def analyze_institutional_positioning(self, options_data):
        """Analyze potential institutional positioning"""
        try:
            # Large block analysis (simplified)
            large_positions = []
            
            for row in options_data:
                call_oi = row.get('call_oi', 0)
                put_oi = row.get('put_oi', 0)
                
                # Detect potentially large institutional positions
                if call_oi > 50000:  # Threshold for large positions
                    large_positions.append({
                        'strike': row['strike'],
                        'type': 'call',
                        'oi': call_oi,
                        'notional_value': call_oi * row.get('call_ltp', 0) * 50  # Assuming lot size 50
                    })
                
                if put_oi > 50000:
                    large_positions.append({
                        'strike': row['strike'],
                        'type': 'put', 
                        'oi': put_oi,
                        'notional_value': put_oi * row.get('put_ltp', 0) * 50
                    })
            
            # Positioning analysis
            total_call_notional = sum(p['notional_value'] for p in large_positions if p['type'] == 'call')
            total_put_notional = sum(p['notional_value'] for p in large_positions if p['type'] == 'put')
            
            positioning_analysis = {
                'large_positions': large_positions,
                'institutional_bias': 'Bullish' if total_call_notional > total_put_notional else 'Bearish',
                'total_call_notional': total_call_notional,
                'total_put_notional': total_put_notional,
                'net_positioning': total_call_notional - total_put_notional
            }
            
            return positioning_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing institutional positioning: {e}")
            return {}
    
    def calculate_risk_metrics(self, options_data, spot_price):
        """Calculate portfolio risk metrics"""
        try:
            # VaR calculation (simplified)
            total_delta = sum(row.get('call_delta', 0) * row.get('call_oi', 0) + 
                             row.get('put_delta', 0) * row.get('put_oi', 0) 
                             for row in options_data)
            
            total_gamma = sum(row.get('call_gamma', 0) * row.get('call_oi', 0) + 
                             row.get('put_gamma', 0) * row.get('put_oi', 0) 
                             for row in options_data)
            
            # Risk scenarios
            scenarios = {
                '1_percent_move': {
                    'up': total_delta * spot_price * 0.01 + 0.5 * total_gamma * (spot_price * 0.01)**2,
                    'down': total_delta * spot_price * (-0.01) + 0.5 * total_gamma * (spot_price * (-0.01))**2
                },
                '2_percent_move': {
                    'up': total_delta * spot_price * 0.02 + 0.5 * total_gamma * (spot_price * 0.02)**2,
                    'down': total_delta * spot_price * (-0.02) + 0.5 * total_gamma * (spot_price * (-0.02))**2
                }
            }
            
            return {
                'portfolio_delta_exposure': total_delta,
                'portfolio_gamma_exposure': total_gamma,
                'risk_scenarios': scenarios,
                'max_single_day_risk': max(abs(scenarios['2_percent_move']['up']), 
                                          abs(scenarios['2_percent_move']['down']))
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            return {}
    
    def generate_market_insights(self, options_data, spot_price):
        """Generate actionable market insights"""
        try:
            insights = []
            
            # Analyze the data
            advanced_greeks = self.calculate_advanced_greeks(options_data, spot_price)
            volatility_analytics = self.calculate_volatility_analytics(options_data)
            flow_patterns = self.analyze_flow_patterns(options_data)
            support_resistance = self.calculate_support_resistance_levels(options_data, spot_price)
            
            # Generate insights based on analysis
            if volatility_analytics.get('iv_spread', 0) > 2:
                insights.append({
                    'type': 'volatility',
                    'severity': 'medium',
                    'title': 'IV Spread Divergence',
                    'description': f"Call-Put IV spread at {volatility_analytics['iv_spread']:.1f}% indicates potential directional bias"
                })
            
            if flow_patterns.get('volume_pcr', 0) > 1.5:
                insights.append({
                    'type': 'flow',
                    'severity': 'high',
                    'title': 'Heavy Put Buying',
                    'description': f"Put volume significantly exceeding calls (PCR: {flow_patterns['volume_pcr']:.2f})"
                })
            
            gamma_wall = advanced_greeks.get('max_gamma_strike')
            if gamma_wall and abs(gamma_wall - spot_price) / spot_price < 0.01:
                insights.append({
                    'type': 'gamma',
                    'severity': 'high',
                    'title': 'Near Gamma Wall',
                    'description': f"Spot price near significant gamma level at {gamma_wall}"
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating market insights: {e}")
            return []
    
    def _calculate_iv_percentile(self, iv_values):
        """Calculate IV percentile rank (simplified)"""
        if not iv_values:
            return 50
        
        current_iv = np.mean(iv_values)
        # Simplified percentile calculation
        return min(max(current_iv * 2, 0), 100)
    
    def _calculate_sentiment_score(self, flow_data):
        """Calculate market sentiment score from flow data"""
        try:
            pcr = flow_data.get('volume_pcr', 1)
            
            # Sentiment score: 0-100 (50 = neutral)
            if pcr < 0.8:
                return 70  # Bullish
            elif pcr > 1.2:
                return 30  # Bearish
            else:
                return 50  # Neutral
                
        except:
            return 50

    def comprehensive_analysis(self, options_data, spot_price, risk_free_rate=0.05):
        """Run comprehensive enhanced analytics"""
        try:
            result = {
                'timestamp': datetime.now().isoformat(),
                'spot_price': spot_price,
                'analytics': {
                    'advanced_greeks': self.calculate_advanced_greeks(options_data, spot_price, risk_free_rate),
                    'volatility_analytics': self.calculate_volatility_analytics(options_data),
                    'flow_patterns': self.analyze_flow_patterns(options_data),
                    'support_resistance': self.calculate_support_resistance_levels(options_data, spot_price),
                    'institutional_positioning': self.analyze_institutional_positioning(options_data),
                    'risk_metrics': self.calculate_risk_metrics(options_data, spot_price),
                    'market_insights': self.generate_market_insights(options_data, spot_price)
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {'error': str(e)}
