import random
import numpy as np
from datetime import datetime, timedelta
import re

class ResearchReportScorer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.sebi_keywords = [
            'insider trading', 'material information', 'price sensitive', 
            'forward looking', 'risks', 'disclosures', 'regulatory',
            'compliance', 'fiduciary', 'conflict of interest'
        ]
        self.geopolitical_keywords = [
            'trade war', 'sanctions', 'geopolitical', 'political instability',
            'regulatory changes', 'government policy', 'international relations',
            'brexit', 'tariffs', 'trade agreements', 'diplomatic tensions'
        ]

    def score_report(self, report_text, analyst, tickers, ohlc_data, plagiarism_score=0.0, ai_probability=0.0):
        # Enhanced scoring with more realistic metrics
        scores = self._calculate_quality_scores(report_text, analyst, tickers)
        
        # Enhanced backtesting with better metrics
        backtest_results = self._enhanced_backtesting(tickers, ohlc_data)
        
        # Calculate sentiment trend
        sentiment_trend = self._calculate_sentiment_trend(report_text)
        
        # NEW: Detailed Quality Metrics Analysis
        detailed_quality_metrics = self._analyze_detailed_quality_metrics(report_text, analyst, tickers)
        
        # NEW: Comprehensive SEBI compliance with detailed breakdown
        sebi_compliance_detailed = self._comprehensive_sebi_compliance_analysis(report_text)
        
        # NEW: Content Guidelines Analysis
        content_guidelines_analysis = self._analyze_content_guidelines(report_text, tickers)
        
        # NEW: Flagged Alerts System
        flagged_alerts = self._generate_flagged_alerts(report_text, scores, sebi_compliance_detailed)
        
        # NEW: Action Items Analysis
        action_items = self._generate_action_items(report_text, sebi_compliance_detailed, content_guidelines_analysis)
        
        # NEW: Geopolitical risk assessment
        geopolitical_assessment = self._assess_geopolitical_risks(report_text, tickers)
        
        # NEW: SEBI compliance check (keeping existing for compatibility)
        sebi_compliance = self._check_sebi_compliance(report_text)
        
        # NEW: Global standards compliance
        global_standards = self._check_global_standards(report_text)
        
        # NEW: Stock Quality Assessment
        stock_quality_assessment = self._assess_stock_quality(tickers, ohlc_data)
        
        # NEW: Plagiarism penalty calculation
        plagiarism_penalty = self._calculate_plagiarism_penalty(plagiarism_score)
        
        # NEW: AI detection penalty calculation
        ai_penalty = self._calculate_ai_penalty(ai_probability)

        # Enhanced weighted average including stock quality and other factors
        base_composite_score = (
            0.16 * scores["factual_accuracy"] +           # Reduced from 0.18
            0.12 * scores["predictive_power"] +           # Reduced from 0.14
            0.09 * (1 - abs(scores["bias_score"])) +      # Reduced from 0.10
            0.09 * scores["originality"] +                # Reduced from 0.10
            0.11 * scores["risk_disclosure"] +            # Reduced from 0.12
            0.07 * scores["transparency"] +               # Reduced from 0.08
            0.09 * geopolitical_assessment["score"] +     # Reduced from 0.10
            0.07 * sebi_compliance["score"] +             # Reduced from 0.08
            0.05 * detailed_quality_metrics["content_quality_score"] +
            0.05 * content_guidelines_analysis["overall_compliance_score"] +
            0.10 * stock_quality_assessment["average_score"]  # NEW: 10% weight for stock quality
        )
        
        # Apply plagiarism and AI penalties
        composite_quality_score = max(0.0, base_composite_score - plagiarism_penalty - ai_penalty)

        return {
            "analyst": analyst,
            "scores": scores,
            "composite_quality_score": round(composite_quality_score, 3),
            "base_composite_score": round(base_composite_score, 3),
            "plagiarism_penalty": round(plagiarism_penalty, 3),
            "plagiarism_score": plagiarism_score,
            "ai_penalty": round(ai_penalty, 3),
            "ai_probability": ai_probability,
            "backtest_results": backtest_results,
            "sentiment_trend": sentiment_trend,
            "detailed_quality_metrics": detailed_quality_metrics,
            "sebi_compliance_detailed": sebi_compliance_detailed,
            "content_guidelines_analysis": content_guidelines_analysis,
            "flagged_alerts": flagged_alerts,
            "action_items": action_items,
            "geopolitical_assessment": geopolitical_assessment,
            "sebi_compliance": sebi_compliance,
            "global_standards": global_standards,
            "stock_quality_assessment": stock_quality_assessment,  # NEW: Include stock quality data
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_quality_scores(self, report_text, analyst, tickers):
        """Calculate quality scores with more sophisticated logic"""
        
        # Simulate LLM-based scoring with more realistic variations
        base_score = 0.7 + random.uniform(0, 0.25)  # Base score between 0.7-0.95
        
        # Analyst-specific adjustments (simulate track record)
        analyst_bonus = self._get_analyst_bonus(analyst)
        
        # Text length and complexity bonus
        text_bonus = min(0.1, len(report_text) / 10000)  # Up to 0.1 bonus for longer reports
        
        # Ticker count consideration
        ticker_bonus = min(0.05, len(tickers) * 0.01)  # Small bonus for covering multiple tickers
        
        scores = {
            "factual_accuracy": min(0.98, base_score + analyst_bonus + text_bonus + random.uniform(-0.1, 0.1)),
            "predictive_power": min(0.95, base_score + analyst_bonus + random.uniform(-0.15, 0.15)),
            "bias_score": random.uniform(-0.6, 0.6),  # Can be negative (bearish) or positive (bullish)
            "originality": min(0.9, base_score - 0.1 + ticker_bonus + random.uniform(-0.2, 0.2)),
            "risk_disclosure": min(0.85, base_score - 0.15 + random.uniform(-0.2, 0.3)),
            "transparency": min(0.95, base_score + text_bonus + random.uniform(-0.1, 0.15))
        }
        
        # Ensure all scores are within valid ranges
        for key, value in scores.items():
            if key == "bias_score":
                scores[key] = max(-1.0, min(1.0, value))
            else:
                scores[key] = max(0.0, min(1.0, value))
        
        return scores

    def _get_analyst_bonus(self, analyst):
        """Simulate analyst track record bonus"""
        analyst_track_record = {
            "Sarah Johnson": 0.15,
            "Michael Chen": 0.12,
            "Emma Rodriguez": 0.10,
            "David Kim": 0.08,
            "James Wilson": 0.05
        }
        return analyst_track_record.get(analyst, random.uniform(-0.05, 0.05))

    def _calculate_plagiarism_penalty(self, plagiarism_score):
        """
        Calculate plagiarism penalty based on similarity score
        
        Penalty structure:
        - 0-30% similarity: No penalty
        - 30-50% similarity: Small penalty (0.05-0.1)
        - 50-70% similarity: Medium penalty (0.1-0.25)
        - 70-85% similarity: High penalty (0.25-0.4)
        - 85%+ similarity: Severe penalty (0.4-0.6)
        """
        if plagiarism_score <= 0.30:
            return 0.0
        elif plagiarism_score <= 0.50:
            # Small penalty: 5-10% reduction
            return 0.05 + (plagiarism_score - 0.30) * 0.25
        elif plagiarism_score <= 0.70:
            # Medium penalty: 10-25% reduction
            return 0.10 + (plagiarism_score - 0.50) * 0.75
        elif plagiarism_score <= 0.85:
            # High penalty: 25-40% reduction
            return 0.25 + (plagiarism_score - 0.70) * 1.0
        else:
            # Severe penalty: 40-60% reduction
            return 0.40 + min(0.20, (plagiarism_score - 0.85) * 1.33)
    
    def _calculate_ai_penalty(self, ai_probability):
        """
        Calculate AI detection penalty based on AI probability
        
        Penalty structure:
        - 0-40% AI probability: No penalty (likely human)
        - 40-60% AI probability: Small penalty (0.02-0.05)
        - 60-75% AI probability: Medium penalty (0.05-0.15)
        - 75-85% AI probability: High penalty (0.15-0.25)
        - 85%+ AI probability: Severe penalty (0.25-0.40)
        """
        if ai_probability <= 0.40:
            return 0.0
        elif ai_probability <= 0.60:
            # Small penalty: 2-5% reduction
            return 0.02 + (ai_probability - 0.40) * 0.15
        elif ai_probability <= 0.75:
            # Medium penalty: 5-15% reduction
            return 0.05 + (ai_probability - 0.60) * 0.67
        elif ai_probability <= 0.85:
            # High penalty: 15-25% reduction
            return 0.15 + (ai_probability - 0.75) * 1.0
        else:
            # Severe penalty: 25-40% reduction
            return 0.25 + min(0.15, (ai_probability - 0.85) * 1.0)

    def _enhanced_backtesting(self, tickers, ohlc_data):
        """Enhanced backtesting with more comprehensive metrics for Indian stocks (.NS)"""
        backtest_results = {}
        
        for ticker, data in ohlc_data.items():
            try:
                current_price = float(data['current_price'])
                high_52w = float(data['52w_high'])
                low_52w = float(data['52w_low'])
                volatility = float(data['volatility'])
                
                # Additional metrics for Indian stocks
                avg_volume = float(data.get('avg_volume', 1000000))
                price_change_percent = float(data.get('price_change_percent', 0))
                data_points = int(data.get('data_points', 0))
                
                # Calculate various performance metrics
                price_range_position = (current_price - low_52w) / (high_52w - low_52w) if high_52w > low_52w else 0.5
                target_achievement = current_price / high_52w if high_52w > 0 else 0
                
                # Indian market specific calculations
                # Classify stock performance based on Indian market standards
                if price_change_percent > 20:
                    performance_category = "Excellent"
                elif price_change_percent > 10:
                    performance_category = "Good"
                elif price_change_percent > 0:
                    performance_category = "Positive"
                elif price_change_percent > -10:
                    performance_category = "Moderate Decline"
                else:
                    performance_category = "Poor"
                
                # Risk assessment for Indian stocks
                if volatility < 0.15:
                    risk_level = "Low"
                elif volatility < 0.25:
                    risk_level = "Medium"
                elif volatility < 0.35:
                    risk_level = "High"
                else:
                    risk_level = "Very High"
                
                # Liquidity assessment based on volume
                if avg_volume > 10000000:
                    liquidity = "High"
                elif avg_volume > 1000000:
                    liquidity = "Medium"
                elif avg_volume > 100000:
                    liquidity = "Low"
                else:
                    liquidity = "Very Low"
                
                # Calculate support and resistance levels
                support_level = low_52w + (high_52w - low_52w) * 0.25
                resistance_level = low_52w + (high_52w - low_52w) * 0.75
                
                # Price momentum indicator
                momentum = "Bullish" if current_price > (high_52w + low_52w) / 2 else "Bearish"
                
                # Indian market specific risk-return metrics
                # Simulated beta relative to NIFTY (assuming market beta of 1.0)
                beta = min(2.0, max(0.5, volatility / 0.20))  # Normalized beta
                
                # Expected return based on Indian market conditions
                risk_free_rate = 0.065  # 6.5% - typical Indian risk-free rate
                market_return = 0.12    # 12% - historical Indian market return
                expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
                
                # Sharpe ratio calculation
                excess_return = price_change_percent / 100
                sharpe_ratio = (excess_return - risk_free_rate) / volatility if volatility > 0 else 0
                
                # Value at Risk (VaR) - 95% confidence level
                var_95 = current_price * volatility * 1.645  # 95% VaR
                
                backtest_results[ticker] = {
                    # Basic price data
                    "current_price": round(current_price, 2),
                    "52w_high": round(high_52w, 2),
                    "52w_low": round(low_52w, 2),
                    "price_change_percent": round(price_change_percent, 2),
                    
                    # Performance metrics
                    "target_achievement": round(target_achievement, 3),
                    "price_range_position": round(price_range_position, 3),
                    "performance_category": performance_category,
                    "momentum": momentum,
                    
                    # Risk metrics
                    "volatility": round(volatility, 4),
                    "risk_level": risk_level,
                    "beta": round(beta, 3),
                    "var_95": round(var_95, 2),
                    
                    # Return metrics
                    "expected_return": round(expected_return, 3),
                    "sharpe_ratio": round(sharpe_ratio, 3),
                    
                    # Market metrics
                    "avg_volume": int(avg_volume),
                    "liquidity": liquidity,
                    "support_level": round(support_level, 2),
                    "resistance_level": round(resistance_level, 2),
                    
                    # Data quality
                    "data_points": data_points,
                    "data_quality": "Good" if data_points > 200 else "Limited" if data_points > 50 else "Poor"
                }
                
            except Exception as e:
                # Fallback data if calculations fail
                backtest_results[ticker] = {
                    "current_price": 100.0,
                    "52w_high": 120.0,
                    "52w_low": 80.0,
                    "price_change_percent": 0.0,
                    "target_achievement": 0.83,
                    "price_range_position": 0.5,
                    "performance_category": "Unknown",
                    "momentum": "Neutral",
                    "volatility": 0.25,
                    "risk_level": "Medium",
                    "beta": 1.0,
                    "var_95": 25.0,
                    "expected_return": 0.10,
                    "sharpe_ratio": 0.20,
                    "avg_volume": 1000000,
                    "liquidity": "Medium",
                    "support_level": 90.0,
                    "resistance_level": 110.0,
                    "data_points": 0,
                    "data_quality": "Error"
                }
        
        return backtest_results

    def _calculate_sentiment_trend(self, report_text):
        """Calculate sentiment trend over time simulation"""
        # Simulate 7-day sentiment trend
        sentiment_trend = []
        base_sentiment = random.uniform(-0.5, 0.5)  # Base sentiment from report
        
        for i in range(7):
            # Add some random variation to simulate daily sentiment changes
            daily_sentiment = base_sentiment + random.uniform(-0.2, 0.2)
            daily_sentiment = max(-1.0, min(1.0, daily_sentiment))  # Clamp to [-1, 1]
            
            sentiment_trend.append({
                "day": i + 1,
                "sentiment": round(daily_sentiment, 3),
                "confidence": round(random.uniform(0.6, 0.95), 3)
            })
        
        return sentiment_trend

    def _assess_geopolitical_risks(self, report_text, tickers):
        """Assess geopolitical risks mentioned in the report"""
        text_lower = report_text.lower()
        risk_factors = []
        risk_score = 0.7  # Base score
        
        # Check for geopolitical keywords
        geopolitical_mentions = 0
        for keyword in self.geopolitical_keywords:
            if keyword in text_lower:
                geopolitical_mentions += 1
                risk_factors.append(keyword)
        
        # Assess risk coverage for Indian market context
        indian_risks = [
            'government policy', 'regulatory changes', 'political instability',
            'trade relations', 'monetary policy', 'fiscal policy'
        ]
        
        indian_risk_coverage = sum(1 for risk in indian_risks if risk in text_lower)
        
        # Calculate risk assessment score
        if geopolitical_mentions > 0:
            risk_score += 0.1
        
        if indian_risk_coverage >= 2:
            risk_score += 0.15
        
        # Check for specific SEBI-required risk disclosures
        required_disclosures = [
            'market risk', 'liquidity risk', 'credit risk', 'operational risk',
            'regulatory risk', 'concentration risk'
        ]
        
        disclosure_coverage = sum(1 for disclosure in required_disclosures if disclosure in text_lower)
        risk_score += (disclosure_coverage / len(required_disclosures)) * 0.15
        
        # Generate improvement suggestions
        improvements = []
        if geopolitical_mentions == 0:
            improvements.append("Add geopolitical risk assessment including global trade impacts")
        
        if indian_risk_coverage < 2:
            improvements.append("Include more India-specific risk factors and policy impacts")
        
        if disclosure_coverage < 4:
            improvements.append("Enhance risk disclosure section with comprehensive risk categories")
        
        return {
            "score": min(1.0, risk_score),
            "risk_factors_identified": risk_factors,
            "geopolitical_mentions": geopolitical_mentions,
            "indian_risk_coverage": indian_risk_coverage,
            "disclosure_coverage": disclosure_coverage,
            "improvements": improvements,
            "risk_level": "High" if geopolitical_mentions > 3 else "Medium" if geopolitical_mentions > 0 else "Low"
        }

    def _check_sebi_compliance(self, report_text):
        """Check SEBI compliance based on research analyst regulations"""
        text_lower = report_text.lower()
        compliance_score = 0.6  # Base score
        compliance_issues = []
        compliance_met = []
        
        # SEBI Research Analyst Regulations 2014 requirements
        sebi_requirements = {
            'analyst_credentials': ['inh0000', 'sebi.*registration.*number', 'research analyst.*license'],
            'disclosures': ['disclosure', 'conflict of interest', 'shareholding', 'compensation'],
            'risk_warnings': ['risk', 'investment decision', 'due diligence', 'market volatility'],
            'price_targets': ['price target', 'target price', 'recommendation period', 'methodology'],
            'research_methodology': ['methodology', 'valuation', 'analysis', 'assumptions'],
            'disclaimers': ['disclaimer', 'not investment advice', 'consult advisor', 'past performance']
        }
        
        # Check each requirement category
        for category, keywords in sebi_requirements.items():
            found_keywords = sum(1 for keyword in keywords if keyword in text_lower)
            if found_keywords > 0:
                compliance_met.append(category)
                compliance_score += 0.05
            else:
                compliance_issues.append(f"Missing {category.replace('_', ' ')}")
        
        # Additional SEBI-specific checks
        mandatory_disclosures = [
            'inh0000', 'conflict of interest', 'shareholding disclosure',
            'price target methodology', 'research disclaimer'
        ]
        
        mandatory_disclosures_found = sum(1 for disclosure in mandatory_disclosures 
                                        if any(word in text_lower for word in disclosure.split()))
        
        compliance_score += (mandatory_disclosures_found / len(mandatory_disclosures)) * 0.2
        
        # Determine overall rating
        if compliance_score >= 0.9:
            overall_rating = "Excellent"
        elif compliance_score >= 0.8:
            overall_rating = "Good"
        elif compliance_score >= 0.7:
            overall_rating = "Fair"
        else:
            overall_rating = "Poor"
        
        return {
            "score": min(1.0, compliance_score),
            "overall_rating": overall_rating,
            "compliance_met": compliance_met,
            "compliance_issues": compliance_issues,
            "mandatory_disclosures_found": mandatory_disclosures_found,
            "total_mandatory": len(mandatory_disclosures)
        }

    def _check_global_standards(self, report_text):
        """Check compliance with global research standards"""
        text_lower = report_text.lower()
        global_score = 0.65  # Base score
        standards_met = []
        standards_missing = []
        
        # Global research standards
        global_standards = {
            'cfa_standards': ['cfa', 'ethical standards', 'professional conduct', 'independence'],
            'iosco_principles': ['transparency', 'fair dealing', 'market integrity'],
            'esg_coverage': ['esg', 'environmental', 'social', 'governance', 'sustainability'],
            'international_accounting': ['ifrs', 'international standards', 'accounting principles'],
            'fair_disclosure': ['material information', 'equal access', 'fair disclosure'],
            'research_independence': ['independence', 'objective analysis', 'unbiased research']
        }
        
        # Check each standard
        for standard, keywords in global_standards.items():
            found_keywords = sum(1 for keyword in keywords if keyword in text_lower)
            if found_keywords > 0:
                standards_met.append(standard)
                global_score += 0.05
            else:
                standards_missing.append(standard.replace('_', ' '))
        
        # ESG coverage check (increasingly important globally)
        esg_keywords = ['environmental impact', 'social responsibility', 'corporate governance', 
                       'sustainability metrics', 'climate risk', 'diversity']
        esg_coverage = sum(1 for keyword in esg_keywords if keyword in text_lower) > 0
        
        if esg_coverage:
            global_score += 0.1
        
        # International perspective check
        international_keywords = ['global markets', 'international exposure', 'currency risk',
                                'cross-border', 'multinational', 'global economy']
        international_perspective = sum(1 for keyword in international_keywords if keyword in text_lower) > 0
        
        if international_perspective:
            global_score += 0.05
        
        # Determine global rating
        if global_score >= 0.9:
            global_rating = "World-class"
        elif global_score >= 0.8:
            global_rating = "International"
        elif global_score >= 0.7:
            global_rating = "Regional"
        else:
            global_rating = "Local"
        
        return {
            "score": min(1.0, global_score),
            "global_rating": global_rating,
            "standards_met": standards_met,
            "standards_missing": standards_missing,
            "esg_coverage": esg_coverage,
            "international_perspective": international_perspective
        }

    def compare_reports(self, reports_data):
        """Compare multiple reports on the same stock side-by-side"""
        if len(reports_data) < 2:
            return {"error": "At least 2 reports are required for comparison"}
        
        comparison_result = {
            "total_reports": len(reports_data),
            "comparison_date": datetime.utcnow().isoformat(),
            "quality_comparison": {},
            "plagiarism_analysis": {},
            "key_differences": [],
            "consensus_analysis": {},
            "divergence_points": [],
            "recommendations": []
        }
        
        # Extract tickers from all reports
        all_tickers = set()
        for report in reports_data:
            if isinstance(report.get('tickers'), list):
                all_tickers.update(report['tickers'])
            elif report.get('tickers'):
                all_tickers.add(report['tickers'])
        
        primary_ticker = list(all_tickers)[0] if all_tickers else "Unknown"
        
        # Perform plagiarism analysis between reports
        plagiarism_matrix = self._calculate_plagiarism_between_reports(reports_data)
        comparison_result["plagiarism_analysis"] = plagiarism_matrix
        
        # Analyze each report
        for i, report in enumerate(reports_data):
            report_id = report.get('id', f'Report_{i+1}')
            analysis = report.get('analysis_result', {})
            
            if isinstance(analysis, str):
                # If analysis_result is a string, create a basic structure
                analysis = {"composite_quality_score": 0.75, "scores": {}}
            
            comparison_result["quality_comparison"][report_id] = {
                "analyst": report.get('analyst', f'Analyst_{i+1}'),
                "date": report.get('created_at', datetime.utcnow().isoformat()),
                "composite_score": analysis.get('composite_quality_score', 0.75),
                "base_composite_score": analysis.get('base_composite_score', analysis.get('composite_quality_score', 0.75)),
                "plagiarism_penalty": analysis.get('plagiarism_penalty', 0.0),
                "plagiarism_score": analysis.get('plagiarism_score', 0.0),
                "factual_accuracy": analysis.get('scores', {}).get('factual_accuracy', 0.8),
                "predictive_power": analysis.get('scores', {}).get('predictive_power', 0.75),
                "bias_score": analysis.get('scores', {}).get('bias_score', 0.0),
                "geopolitical_score": analysis.get('geopolitical_assessment', {}).get('score', 0.7),
                "sebi_compliance": analysis.get('sebi_compliance', {}).get('score', 0.75),
                "global_standards": analysis.get('global_standards', {}).get('score', 0.7)
            }
        
        # Calculate consensus metrics
        quality_scores = [data["composite_score"] for data in comparison_result["quality_comparison"].values()]
        bias_scores = [data["bias_score"] for data in comparison_result["quality_comparison"].values()]
        plagiarism_scores = [data["plagiarism_score"] for data in comparison_result["quality_comparison"].values()]
        plagiarism_penalties = [data["plagiarism_penalty"] for data in comparison_result["quality_comparison"].values()]
        
        comparison_result["consensus_analysis"] = {
            "average_quality": round(np.mean(quality_scores), 3),
            "quality_std_dev": round(np.std(quality_scores), 3),
            "quality_range": [round(min(quality_scores), 3), round(max(quality_scores), 3)],
            "consensus_bias": round(np.mean(bias_scores), 3),
            "bias_disagreement": round(np.std(bias_scores), 3),
            "average_plagiarism_score": round(np.mean(plagiarism_scores), 3),
            "max_plagiarism_score": round(max(plagiarism_scores), 3),
            "total_plagiarism_penalty": round(sum(plagiarism_penalties), 3)
        }
        
        # Identify key differences and divergence points
        if comparison_result["consensus_analysis"]["quality_std_dev"] > 0.15:
            comparison_result["divergence_points"].append("Significant quality score disagreement")
        
        if comparison_result["consensus_analysis"]["bias_disagreement"] > 0.4:
            comparison_result["divergence_points"].append("Major bias/sentiment disagreement")
        
        if comparison_result["consensus_analysis"]["max_plagiarism_score"] > 0.50:
            comparison_result["divergence_points"].append("High plagiarism similarity detected between reports")
        
        # Generate recommendations
        if comparison_result["consensus_analysis"]["quality_std_dev"] > 0.2:
            comparison_result["recommendations"].append("Review methodology differences between analysts")
        
        if abs(comparison_result["consensus_analysis"]["consensus_bias"]) > 0.5:
            comparison_result["recommendations"].append("Consider potential market bias in recommendations")
        
        if comparison_result["consensus_analysis"]["average_quality"] < 0.7:
            comparison_result["recommendations"].append("Overall report quality needs improvement")
        
        if comparison_result["consensus_analysis"]["max_plagiarism_score"] > 0.70:
            comparison_result["recommendations"].append("⚠️ Critical: High plagiarism detected - Review content originality")
        elif comparison_result["consensus_analysis"]["average_plagiarism_score"] > 0.40:
            comparison_result["recommendations"].append("⚠️ Moderate plagiarism detected - Ensure content originality")
        
        if comparison_result["consensus_analysis"]["total_plagiarism_penalty"] > 0.20:
            comparison_result["recommendations"].append("Significant quality score penalties due to plagiarism - Focus on original content")
        
        # Add improvement suggestions based on the lowest scoring areas
        geopolitical_scores = [data["geopolitical_score"] for data in comparison_result["quality_comparison"].values()]
        sebi_scores = [data["sebi_compliance"] for data in comparison_result["quality_comparison"].values()]
        
        if np.mean(geopolitical_scores) < 0.7:
            comparison_result["recommendations"].append("Enhance geopolitical risk assessment across all reports")
        
        if np.mean(sebi_scores) < 0.8:
            comparison_result["recommendations"].append("Improve SEBI compliance documentation")
        
        return comparison_result
    
    def _calculate_plagiarism_between_reports(self, reports_data):
        """
        Calculate plagiarism similarity matrix between all reports
        """
        plagiarism_matrix = {
            "similarity_matrix": {},
            "high_similarity_pairs": [],
            "summary": {
                "max_similarity": 0.0,
                "average_similarity": 0.0,
                "total_comparisons": 0
            }
        }
        
        try:
            similarities = []
            
            for i, report1 in enumerate(reports_data):
                report1_id = report1.get('id', f'Report_{i+1}')
                plagiarism_matrix["similarity_matrix"][report1_id] = {}
                
                for j, report2 in enumerate(reports_data):
                    report2_id = report2.get('id', f'Report_{j+1}')
                    
                    if i == j:
                        # Same report
                        similarity = 1.0
                    else:
                        # Calculate similarity between different reports
                        text1 = report1.get('original_text', '')
                        text2 = report2.get('original_text', '')
                        similarity = self._calculate_text_similarity(text1, text2)
                        
                        if i < j:  # Avoid duplicate comparisons
                            similarities.append(similarity)
                            plagiarism_matrix["summary"]["total_comparisons"] += 1
                            
                            # Track high similarity pairs
                            if similarity > 0.30:  # Above 30% similarity threshold
                                plagiarism_matrix["high_similarity_pairs"].append({
                                    "report1_id": report1_id,
                                    "report1_analyst": report1.get('analyst', 'Unknown'),
                                    "report2_id": report2_id,
                                    "report2_analyst": report2.get('analyst', 'Unknown'),
                                    "similarity": round(similarity, 3),
                                    "severity": self._get_similarity_severity(similarity)
                                })
                    
                    plagiarism_matrix["similarity_matrix"][report1_id][report2_id] = round(similarity, 3)
            
            # Calculate summary statistics
            if similarities:
                plagiarism_matrix["summary"]["max_similarity"] = round(max(similarities), 3)
                plagiarism_matrix["summary"]["average_similarity"] = round(sum(similarities) / len(similarities), 3)
            
            # Sort high similarity pairs by similarity score
            plagiarism_matrix["high_similarity_pairs"].sort(key=lambda x: x["similarity"], reverse=True)
            
        except Exception as e:
            plagiarism_matrix["error"] = f"Plagiarism calculation failed: {str(e)}"
        
        return plagiarism_matrix
    
    def _calculate_text_similarity(self, text1, text2):
        """
        Calculate similarity between two texts using word overlap
        """
        if not text1 or not text2:
            return 0.0
        
        # Tokenize and normalize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if len(union) > 0 else 0.0
    
    def _get_similarity_severity(self, similarity):
        """
        Classify similarity severity
        """
        if similarity >= 0.85:
            return "Critical"
        elif similarity >= 0.70:
            return "High"
        elif similarity >= 0.50:
            return "Medium"
        elif similarity >= 0.30:
            return "Low"
        else:
            return "Minimal"
    
    def _analyze_detailed_quality_metrics(self, report_text, analyst, tickers):
        """Comprehensive detailed quality metrics analysis"""
        
        # Basic text analysis
        word_count = len(report_text.split())
        sentence_count = len(re.split(r'[.!?]+', report_text))
        paragraph_count = len([p for p in report_text.split('\n\n') if p.strip()])
        
        # Content depth analysis
        financial_terms = [
            'revenue', 'profit', 'ebitda', 'eps', 'pe ratio', 'debt', 'cash flow',
            'margin', 'roa', 'roe', 'working capital', 'capex', 'valuation'
        ]
        technical_terms = [
            'support', 'resistance', 'moving average', 'rsi', 'macd', 'volume',
            'trend', 'breakout', 'momentum', 'bollinger bands'
        ]
        
        text_lower = report_text.lower()
        financial_depth = sum(1 for term in financial_terms if term in text_lower)
        technical_depth = sum(1 for term in technical_terms if term in text_lower)
        
        # Data citations and sources
        citation_patterns = [
            r'source:', r'data from', r'according to', r'as per', r'bloomberg',
            r'reuters', r'company reports', r'annual report', r'quarterly results'
        ]
        citations_found = sum(1 for pattern in citation_patterns 
                            if re.search(pattern, text_lower))
        
        # Price target analysis
        price_target_patterns = [
            r'target price.*₹?\d+', r'price target.*₹?\d+', r'tp.*₹?\d+',
            r'fair value.*₹?\d+', r'intrinsic value.*₹?\d+'
        ]
        price_targets_found = sum(1 for pattern in price_target_patterns 
                                if re.search(pattern, text_lower))
        
        # Timeline specifications
        timeline_patterns = [
            r'\d+\s*(month|year|quarter)', r'by\s+\d{4}', r'within\s+\d+',
            r'next\s+\d+', r'over\s+\d+', r'short.{0,10}term', r'long.{0,10}term'
        ]
        timeline_specifications = sum(1 for pattern in timeline_patterns 
                                    if re.search(pattern, text_lower))
        
        # Risk mentions analysis
        risk_keywords = [
            'risk', 'volatility', 'uncertainty', 'challenge', 'threat',
            'downside', 'concern', 'caution', 'warning', 'adverse'
        ]
        risk_mentions = sum(1 for keyword in risk_keywords if keyword in text_lower)
        
        # Calculate content quality score
        content_quality_factors = {
            'word_count_adequacy': min(1.0, word_count / 1000),  # Optimal at 1000+ words
            'financial_depth': min(1.0, financial_depth / 8),   # 8+ financial terms
            'technical_depth': min(1.0, technical_depth / 5),   # 5+ technical terms
            'citation_quality': min(1.0, citations_found / 3),  # 3+ citations
            'price_target_clarity': min(1.0, price_targets_found / 1),  # At least 1 target
            'timeline_clarity': min(1.0, timeline_specifications / 2),  # 2+ timelines
            'risk_awareness': min(1.0, risk_mentions / 5)       # 5+ risk mentions
        }
        
        content_quality_score = sum(content_quality_factors.values()) / len(content_quality_factors)
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "paragraph_count": paragraph_count,
            "financial_depth_score": financial_depth,
            "technical_depth_score": technical_depth,
            "citations_found": citations_found,
            "price_targets_identified": price_targets_found,
            "timeline_specifications": timeline_specifications,
            "risk_mentions": risk_mentions,
            "content_quality_score": round(content_quality_score, 3),
            "content_quality_breakdown": content_quality_factors,
            "readability_metrics": {
                "avg_words_per_sentence": round(word_count / max(sentence_count, 1), 1),
                "avg_sentences_per_paragraph": round(sentence_count / max(paragraph_count, 1), 1)
            }
        }

    def _comprehensive_sebi_compliance_analysis(self, report_text):
        """Comprehensive SEBI compliance analysis with detailed breakdown"""
        text_lower = report_text.lower()
        
        # Disclosure Requirements Analysis
        disclosure_requirements = {
            "sebi_registration": {
                "keywords": ["inh0000", "sebi.*registration.*inh", "research analyst.*inh", "ra.*license.*inh"],
                "found": False,
                "score": 0,
                "importance": "Critical"
            },
            "conflict_of_interest": {
                "keywords": ["conflict of interest", "holdings", "financial interest", "personal stake"],
                "found": False,
                "score": 0,
                "importance": "Critical"
            },
            "shareholding_disclosure": {
                "keywords": ["shareholding", "holds shares", "equity position", "ownership"],
                "found": False,
                "score": 0,
                "importance": "High"
            },
            "compensation_disclosure": {
                "keywords": ["compensation", "fees", "payment", "remuneration"],
                "found": False,
                "score": 0,
                "importance": "High"
            },
            "research_methodology": {
                "keywords": ["methodology", "valuation method", "analysis approach", "research process"],
                "found": False,
                "score": 0,
                "importance": "Medium"
            },
            "price_target_methodology": {
                "keywords": ["target price methodology", "valuation basis", "calculation method"],
                "found": False,
                "score": 0,
                "importance": "High"
            }
        }
        
        # Risk Disclosure Analysis
        risk_disclosure_requirements = {
            "market_risk": {
                "keywords": ["market risk", "market volatility", "systematic risk"],
                "found": False,
                "score": 0
            },
            "liquidity_risk": {
                "keywords": ["liquidity risk", "trading volume", "market liquidity"],
                "found": False,
                "score": 0
            },
            "credit_risk": {
                "keywords": ["credit risk", "default risk", "counterparty risk"],
                "found": False,
                "score": 0
            },
            "operational_risk": {
                "keywords": ["operational risk", "business risk", "management risk"],
                "found": False,
                "score": 0
            },
            "regulatory_risk": {
                "keywords": ["regulatory risk", "policy changes", "compliance risk"],
                "found": False,
                "score": 0
            },
            "concentration_risk": {
                "keywords": ["concentration risk", "sector risk", "diversification"],
                "found": False,
                "score": 0
            }
        }
        
        # Analyst Credentials Check
        analyst_credentials = {
            "sebi_certification": {
                "keywords": ["sebi certified", "sebi registered", "research analyst license"],
                "found": False,
                "score": 0
            },
            "professional_qualification": {
                "keywords": ["cfa", "ca", "mba finance", "chartered accountant"],
                "found": False,
                "score": 0
            },
            "experience_mentioned": {
                "keywords": ["years experience", "expertise", "specialization"],
                "found": False,
                "score": 0
            }
        }
        
        # Company Disclaimers Check
        company_disclaimers = {
            "investment_advice_disclaimer": {
                "keywords": ["not investment advice", "consult advisor", "professional advice"],
                "found": False,
                "score": 0
            },
            "past_performance_disclaimer": {
                "keywords": ["past performance", "future results", "no guarantee"],
                "found": False,
                "score": 0
            },
            "risk_warning": {
                "keywords": ["risk warning", "investment risks", "market volatility"],
                "found": False,
                "score": 0
            },
            "research_limitations": {
                "keywords": ["limitations", "assumptions", "estimates"],
                "found": False,
                "score": 0
            }
        }
        
        # Check all requirements
        for category_dict in [disclosure_requirements, risk_disclosure_requirements, 
                             analyst_credentials, company_disclaimers]:
            for item_key, item_data in category_dict.items():
                for keyword in item_data["keywords"]:
                    if keyword in text_lower:
                        item_data["found"] = True
                        item_data["score"] = 1.0
                        break
                else:
                    item_data["score"] = 0.0
        
        # Calculate compliance scores
        disclosure_score = sum(item["score"] for item in disclosure_requirements.values()) / len(disclosure_requirements)
        risk_disclosure_score = sum(item["score"] for item in risk_disclosure_requirements.values()) / len(risk_disclosure_requirements)
        credentials_score = sum(item["score"] for item in analyst_credentials.values()) / len(analyst_credentials)
        disclaimers_score = sum(item["score"] for item in company_disclaimers.values()) / len(company_disclaimers)
        
        # Overall compliance score with weighted importance
        overall_score = (
            0.35 * disclosure_score +      # Most important
            0.25 * risk_disclosure_score + # Very important
            0.20 * disclaimers_score +     # Important
            0.20 * credentials_score       # Important
        )
        
        # Generate compliance rating
        if overall_score >= 0.9:
            compliance_rating = "Excellent"
        elif overall_score >= 0.8:
            compliance_rating = "Good"
        elif overall_score >= 0.7:
            compliance_rating = "Satisfactory"
        elif overall_score >= 0.6:
            compliance_rating = "Needs Improvement"
        else:
            compliance_rating = "Poor"
        
        return {
            "overall_compliance_score": round(overall_score, 3),
            "compliance_rating": compliance_rating,
            "disclosure_requirements": disclosure_requirements,
            "risk_disclosure_requirements": risk_disclosure_requirements,
            "analyst_credentials": analyst_credentials,
            "company_disclaimers": company_disclaimers,
            "category_scores": {
                "disclosure_score": round(disclosure_score, 3),
                "risk_disclosure_score": round(risk_disclosure_score, 3),
                "credentials_score": round(credentials_score, 3),
                "disclaimers_score": round(disclaimers_score, 3)
            }
        }

    def _analyze_content_guidelines(self, report_text, tickers):
        """Analyze content guidelines compliance"""
        text_lower = report_text.lower()
        
        # Factual Accuracy Analysis
        factual_accuracy_indicators = {
            "data_sources_cited": sum(1 for source in ["bloomberg", "reuters", "company report", "annual report"] 
                                    if source in text_lower),
            "numerical_data_present": len(re.findall(r'\d+(?:\.\d+)?%|\₹\d+(?:,\d+)*(?:\.\d+)?', report_text)),
            "financial_metrics_used": sum(1 for metric in ["pe", "roe", "roa", "ebitda", "revenue"] 
                                        if metric in text_lower),
            "verification_statements": sum(1 for stmt in ["verified", "confirmed", "as per records"] 
                                         if stmt in text_lower)
        }
        
        # Bias Control Analysis
        bias_control_indicators = {
            "balanced_perspective": sum(1 for term in ["however", "on the other hand", "despite", "although"] 
                                      if term in text_lower),
            "risk_acknowledgment": sum(1 for risk in ["risk", "uncertainty", "challenge", "downside"] 
                                     if risk in text_lower),
            "neutral_language": 1.0 - min(1.0, sum(1 for bias in ["definitely", "certainly", "guaranteed", "sure shot"] 
                                                  if bias in text_lower) / 10),
            "multiple_scenarios": sum(1 for scenario in ["best case", "worst case", "base case", "scenario"] 
                                    if scenario in text_lower)
        }
        
        # Price Target Justification Analysis
        price_target_justification = {
            "methodology_explained": sum(1 for method in ["dcf", "pe multiple", "ev/ebitda", "sum of parts"] 
                                       if method in text_lower),
            "assumptions_stated": sum(1 for assumption in ["assuming", "based on", "estimates", "projections"] 
                                    if assumption in text_lower),
            "peer_comparison": sum(1 for comp in ["peer", "industry average", "comparable", "benchmark"] 
                                 if comp in text_lower),
            "sensitivity_analysis": sum(1 for sens in ["sensitivity", "range", "upside", "downside potential"] 
                                      if sens in text_lower)
        }
        
        # Timeline Specification Analysis
        timeline_specification = {
            "specific_timeframes": len(re.findall(r'\d+\s*(month|year|quarter)', text_lower)),
            "target_achievement_period": sum(1 for period in ["12 months", "1 year", "2 years", "by 2025"] 
                                           if period in text_lower),
            "milestone_dates": len(re.findall(r'by\s+\w+\s+\d{4}|\d{1,2}/\d{4}', text_lower)),
            "review_periods": sum(1 for review in ["quarterly review", "annual review", "monitoring"] 
                                if review in text_lower)
        }
        
        # Calculate compliance scores for each guideline
        guidelines_scores = {}
        
        # Factual Accuracy Score
        max_sources = 5
        max_metrics = 10
        factual_score = min(1.0, (
            factual_accuracy_indicators["data_sources_cited"] / max_sources * 0.3 +
            min(1.0, factual_accuracy_indicators["numerical_data_present"] / 20) * 0.4 +
            min(1.0, factual_accuracy_indicators["financial_metrics_used"] / max_metrics) * 0.2 +
            min(1.0, factual_accuracy_indicators["verification_statements"] / 3) * 0.1
        ))
        guidelines_scores["factual_accuracy"] = factual_score
        
        # Bias Control Score
        bias_score = min(1.0, (
            min(1.0, bias_control_indicators["balanced_perspective"] / 5) * 0.3 +
            min(1.0, bias_control_indicators["risk_acknowledgment"] / 10) * 0.3 +
            bias_control_indicators["neutral_language"] * 0.2 +
            min(1.0, bias_control_indicators["multiple_scenarios"] / 3) * 0.2
        ))
        guidelines_scores["bias_control"] = bias_score
        
        # Price Target Justification Score
        target_score = min(1.0, (
            min(1.0, price_target_justification["methodology_explained"] / 2) * 0.4 +
            min(1.0, price_target_justification["assumptions_stated"] / 5) * 0.3 +
            min(1.0, price_target_justification["peer_comparison"] / 3) * 0.2 +
            min(1.0, price_target_justification["sensitivity_analysis"] / 2) * 0.1
        ))
        guidelines_scores["price_target_justification"] = target_score
        
        # Timeline Specification Score
        timeline_score = min(1.0, (
            min(1.0, timeline_specification["specific_timeframes"] / 5) * 0.4 +
            min(1.0, timeline_specification["target_achievement_period"] / 2) * 0.3 +
            min(1.0, timeline_specification["milestone_dates"] / 3) * 0.2 +
            min(1.0, timeline_specification["review_periods"] / 2) * 0.1
        ))
        guidelines_scores["timeline_specification"] = timeline_score
        
        # Overall compliance score
        overall_compliance_score = sum(guidelines_scores.values()) / len(guidelines_scores)
        
        return {
            "overall_compliance_score": round(overall_compliance_score, 3),
            "guidelines_scores": {k: round(v, 3) for k, v in guidelines_scores.items()},
            "detailed_analysis": {
                "factual_accuracy_indicators": factual_accuracy_indicators,
                "bias_control_indicators": bias_control_indicators,
                "price_target_justification": price_target_justification,
                "timeline_specification": timeline_specification
            }
        }

    def _generate_flagged_alerts(self, report_text, base_scores, sebi_compliance):
        """Generate flagged alerts for quality and compliance issues"""
        alerts = []
        text_lower = report_text.lower()
        
        # Critical Alerts (High Priority)
        if sebi_compliance["overall_compliance_score"] < 0.6:
            alerts.append({
                "type": "Critical",
                "category": "SEBI Compliance",
                "message": "Severe SEBI compliance deficiencies detected",
                "details": f"Compliance score: {sebi_compliance['overall_compliance_score']:.1%}",
                "action_required": "Immediate compliance review required"
            })
        
        if base_scores.get("factual_accuracy", 1.0) < 0.6:
            alerts.append({
                "type": "Critical",
                "category": "Factual Accuracy",
                "message": "Low factual accuracy score detected",
                "details": f"Accuracy score: {base_scores['factual_accuracy']:.1%}",
                "action_required": "Verify all data sources and calculations"
            })
        
        # High Priority Alerts
        if not sebi_compliance["disclosure_requirements"]["conflict_of_interest"]["found"]:
            alerts.append({
                "type": "High",
                "category": "Disclosure",
                "message": "Missing conflict of interest disclosure",
                "details": "No conflict of interest statement found",
                "action_required": "Add comprehensive conflict of interest disclosure"
            })
        
        if not sebi_compliance["risk_disclosure_requirements"]["market_risk"]["found"]:
            alerts.append({
                "type": "High",
                "category": "Risk Disclosure",
                "message": "Insufficient market risk disclosure",
                "details": "Market risk warnings not adequately covered",
                "action_required": "Add comprehensive market risk warnings"
            })
        
        # Medium Priority Alerts
        if "target price" not in text_lower and "price target" not in text_lower:
            alerts.append({
                "type": "Medium",
                "category": "Price Target",
                "message": "No clear price target specified",
                "details": "Price target not clearly mentioned",
                "action_required": "Specify clear price target with methodology"
            })
        
        if len(re.findall(r'\d+\s*(month|year)', text_lower)) == 0:
            alerts.append({
                "type": "Medium",
                "category": "Timeline",
                "message": "Timeline specification unclear",
                "details": "Investment timeline not clearly specified",
                "action_required": "Add specific timeframe for recommendations"
            })
        
        # Low Priority Alerts
        word_count = len(report_text.split())
        if word_count < 500:
            alerts.append({
                "type": "Low",
                "category": "Content Depth",
                "message": "Report may be too brief",
                "details": f"Word count: {word_count} (recommended: 500+)",
                "action_required": "Consider expanding analysis depth"
            })
        
        if abs(base_scores.get("bias_score", 0)) > 0.7:
            alerts.append({
                "type": "Low",
                "category": "Bias Control",
                "message": "Potential bias detected in analysis",
                "details": f"Bias score: {base_scores['bias_score']:.2f}",
                "action_required": "Review for balanced perspective"
            })
        
        # ESG and Sustainability Alerts
        esg_terms = ["esg", "environmental", "social", "governance", "sustainability"]
        if not any(term in text_lower for term in esg_terms):
            alerts.append({
                "type": "Low",
                "category": "ESG Coverage",
                "message": "No ESG considerations mentioned",
                "details": "Environmental, Social, Governance factors not discussed",
                "action_required": "Consider adding ESG analysis for comprehensive coverage"
            })
        
        return {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a["type"] == "Critical"]),
            "high_priority_alerts": len([a for a in alerts if a["type"] == "High"]),
            "medium_priority_alerts": len([a for a in alerts if a["type"] == "Medium"]),
            "low_priority_alerts": len([a for a in alerts if a["type"] == "Low"]),
            "alerts": alerts
        }

    def _generate_action_items(self, report_text, sebi_compliance, content_guidelines):
        """Generate specific action items for report improvement"""
        action_items = {
            "immediate_actions": [],
            "compliance_actions": [],
            "content_enhancement": [],
            "disclosure_improvements": [],
            "risk_management": []
        }
        
        text_lower = report_text.lower()
        
        # Immediate Actions (Critical Issues)
        if sebi_compliance["overall_compliance_score"] < 0.7:
            action_items["immediate_actions"].append({
                "priority": "Critical",
                "action": "Enhance SEBI Compliance Framework",
                "description": "Implement comprehensive SEBI compliance checklist for all reports",
                "timeline": "Immediate",
                "responsible": "Compliance Team"
            })
        
        if not sebi_compliance["disclosure_requirements"]["sebi_registration"]["found"]:
            action_items["immediate_actions"].append({
                "priority": "Critical",
                "action": "Add SEBI Registration Disclosure",
                "description": "Include clear SEBI research analyst registration details",
                "timeline": "Before publication",
                "responsible": "Legal/Compliance"
            })
        
        # Compliance Actions
        missing_disclosures = [k for k, v in sebi_compliance["disclosure_requirements"].items() if not v["found"]]
        for disclosure in missing_disclosures:
            action_items["compliance_actions"].append({
                "priority": "High",
                "action": f"Add {disclosure.replace('_', ' ').title()} Disclosure",
                "description": f"Include comprehensive {disclosure.replace('_', ' ')} statement",
                "timeline": "Next revision",
                "responsible": "Research Analyst"
            })
        
        missing_risks = [k for k, v in sebi_compliance["risk_disclosure_requirements"].items() if not v["found"]]
        for risk in missing_risks[:3]:  # Top 3 missing risks
            action_items["compliance_actions"].append({
                "priority": "High",
                "action": f"Enhance {risk.replace('_', ' ').title()} Disclosure",
                "description": f"Add detailed {risk.replace('_', ' ')} warnings and mitigation strategies",
                "timeline": "Next revision",
                "responsible": "Risk Management"
            })
        
        # Content Enhancement
        if content_guidelines["guidelines_scores"]["factual_accuracy"] < 0.7:
            action_items["content_enhancement"].append({
                "priority": "High",
                "action": "Improve Data Citation and Verification",
                "description": "Add more credible data sources and verification statements",
                "timeline": "Next revision",
                "responsible": "Research Team"
            })
        
        if content_guidelines["guidelines_scores"]["price_target_justification"] < 0.6:
            action_items["content_enhancement"].append({
                "priority": "High",
                "action": "Strengthen Price Target Methodology",
                "description": "Provide detailed valuation methodology and assumptions",
                "timeline": "Next revision",
                "responsible": "Valuation Team"
            })
        
        if content_guidelines["guidelines_scores"]["timeline_specification"] < 0.5:
            action_items["content_enhancement"].append({
                "priority": "Medium",
                "action": "Specify Investment Timeline Clearly",
                "description": "Add specific timeframes for target achievement and review periods",
                "timeline": "Next revision",
                "responsible": "Research Analyst"
            })
        
        # Disclosure Improvements
        if not sebi_compliance["company_disclaimers"]["investment_advice_disclaimer"]["found"]:
            action_items["disclosure_improvements"].append({
                "priority": "High",
                "action": "Add Investment Advice Disclaimer",
                "description": "Include clear disclaimer that report is not personalized investment advice",
                "timeline": "Immediate",
                "responsible": "Legal Team"
            })
        
        if not sebi_compliance["analyst_credentials"]["sebi_certification"]["found"]:
            action_items["disclosure_improvements"].append({
                "priority": "Medium",
                "action": "Include Analyst Credentials",
                "description": "Add analyst qualifications and SEBI certification details",
                "timeline": "Next revision",
                "responsible": "HR/Compliance"
            })
        
        # Risk Management Actions
        if sebi_compliance["category_scores"]["risk_disclosure_score"] < 0.6:
            action_items["risk_management"].append({
                "priority": "High",
                "action": "Comprehensive Risk Disclosure Review",
                "description": "Implement systematic risk identification and disclosure process",
                "timeline": "Within 2 weeks",
                "responsible": "Risk Management Team"
            })
        
        # ESG and Sustainability Actions
        esg_terms = ["esg", "environmental", "social", "governance"]
        if not any(term in text_lower for term in esg_terms):
            action_items["content_enhancement"].append({
                "priority": "Low",
                "action": "Integrate ESG Analysis",
                "description": "Add Environmental, Social, and Governance considerations to analysis",
                "timeline": "Future reports",
                "responsible": "Research Team"
            })
        
        return action_items

    def _assess_stock_quality(self, tickers, ohlc_data):
        """
        Assess the fundamental quality of stocks mentioned in the report
        Returns comprehensive stock quality metrics that contribute to the composite score
        """
        try:
            import yfinance as yf
        except ImportError:
            # Fallback if yfinance is not available
            return {
                "average_score": 0.75,
                "total_stocks": len(tickers),
                "stock_details": {},
                "quality_distribution": {"High Quality": 0, "Good Quality": 0, "Average Quality": 0, "Below Average": 0},
                "error": "yfinance module not available for detailed stock quality assessment"
            }
        
        if not tickers:
            return {
                "average_score": 0.5,
                "total_stocks": 0,
                "stock_details": {},
                "quality_distribution": {"High Quality": 0, "Good Quality": 0, "Average Quality": 0, "Below Average": 0},
                "message": "No stocks to analyze"
            }
        
        stock_quality_scores = []
        stock_details = {}
        quality_distribution = {"High Quality": 0, "Good Quality": 0, "Average Quality": 0, "Below Average": 0}
        
        for ticker in tickers:
            try:
                # Get stock information
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1y")
                
                if hist.empty:
                    # Use OHLC data if available
                    stock_quality_data = self._calculate_quality_from_ohlc(ticker, ohlc_data.get(ticker, {}))
                else:
                    # Calculate comprehensive quality score
                    stock_quality_data = self._calculate_comprehensive_stock_quality(ticker, info, hist)
                
                # Add to collections
                stock_quality_scores.append(stock_quality_data["quality_score"])
                stock_details[ticker] = stock_quality_data
                
                # Update quality distribution
                quality_rating = stock_quality_data["quality_rating"]
                if "High Quality" in quality_rating or "Excellent" in quality_rating:
                    quality_distribution["High Quality"] += 1
                elif "Good Quality" in quality_rating:
                    quality_distribution["Good Quality"] += 1
                elif "Average" in quality_rating:
                    quality_distribution["Average Quality"] += 1
                else:
                    quality_distribution["Below Average"] += 1
                
            except Exception as e:
                # Fallback for failed stock analysis
                stock_quality_scores.append(0.6)  # Neutral score
                stock_details[ticker] = {
                    "quality_score": 0.6,
                    "quality_rating": "Unable to assess",
                    "error": str(e),
                    "company_name": ticker.replace('.NS', '').replace('.BO', ''),
                    "assessment_date": datetime.utcnow().isoformat()
                }
                quality_distribution["Average Quality"] += 1
        
        # Calculate average quality score
        average_score = sum(stock_quality_scores) / len(stock_quality_scores) if stock_quality_scores else 0.5
        
        # Generate portfolio-level insights
        portfolio_insights = self._generate_portfolio_quality_insights(stock_details, quality_distribution)
        
        return {
            "average_score": round(average_score, 3),
            "total_stocks": len(tickers),
            "stock_details": stock_details,
            "quality_distribution": quality_distribution,
            "portfolio_insights": portfolio_insights,
            "assessment_date": datetime.utcnow().isoformat(),
            "quality_summary": {
                "high_quality_percentage": round((quality_distribution["High Quality"] / len(tickers)) * 100, 1),
                "above_average_percentage": round(((quality_distribution["High Quality"] + quality_distribution["Good Quality"]) / len(tickers)) * 100, 1),
                "needs_attention": [ticker for ticker, data in stock_details.items() if data["quality_score"] < 0.4]
            }
        }

    def _calculate_comprehensive_stock_quality(self, ticker, info, hist_data):
        """
        Calculate comprehensive stock quality score using fundamental and technical metrics
        """
        try:
            quality_factors = {}
            total_score = 0
            max_possible_score = 0
            
            # Basic company information
            company_name = info.get('longName', ticker.replace('.NS', '').replace('.BO', ''))
            sector = info.get('sector', 'Unknown')
            market_cap = info.get('marketCap', 0)
            
            # 1. Profitability Assessment (30 points)
            profitability_score = 0
            if info.get('returnOnEquity') and info['returnOnEquity'] > 0:
                roe = info['returnOnEquity']
                if roe >= 0.20:
                    profitability_score += 10
                elif roe >= 0.15:
                    profitability_score += 8
                elif roe >= 0.10:
                    profitability_score += 6
                elif roe >= 0.05:
                    profitability_score += 3
            
            if info.get('profitMargins') and info['profitMargins'] > 0:
                profit_margin = info['profitMargins']
                if profit_margin >= 0.15:
                    profitability_score += 10
                elif profit_margin >= 0.10:
                    profitability_score += 8
                elif profit_margin >= 0.05:
                    profitability_score += 5
                elif profit_margin >= 0.02:
                    profitability_score += 2
            
            if info.get('operatingMargins') and info['operatingMargins'] > 0:
                operating_margin = info['operatingMargins']
                if operating_margin >= 0.20:
                    profitability_score += 10
                elif operating_margin >= 0.15:
                    profitability_score += 8
                elif operating_margin >= 0.10:
                    profitability_score += 5
                elif operating_margin >= 0.05:
                    profitability_score += 3
            
            quality_factors['profitability'] = min(profitability_score, 30)
            max_possible_score += 30
            
            # 2. Financial Health Assessment (25 points)
            financial_health_score = 0
            
            # Debt management
            if info.get('debtToEquity') is not None:
                debt_to_equity = info['debtToEquity']
                if debt_to_equity <= 0.3:
                    financial_health_score += 10
                elif debt_to_equity <= 0.6:
                    financial_health_score += 7
                elif debt_to_equity <= 1.0:
                    financial_health_score += 4
            
            # Liquidity
            if info.get('currentRatio') and info['currentRatio'] > 0:
                current_ratio = info['currentRatio']
                if current_ratio >= 2.0:
                    financial_health_score += 8
                elif current_ratio >= 1.5:
                    financial_health_score += 6
                elif current_ratio >= 1.2:
                    financial_health_score += 3
            
            # Cash flow
            if info.get('freeCashflow') and info['freeCashflow'] > 0:
                financial_health_score += 7
            
            quality_factors['financial_health'] = min(financial_health_score, 25)
            max_possible_score += 25
            
            # 3. Valuation Assessment (20 points)
            valuation_score = 0
            
            if info.get('trailingPE') and info['trailingPE'] > 0:
                pe_ratio = info['trailingPE']
                if pe_ratio <= 15:
                    valuation_score += 10
                elif pe_ratio <= 25:
                    valuation_score += 7
                elif pe_ratio <= 35:
                    valuation_score += 4
            
            if info.get('priceToBook') and info['priceToBook'] > 0:
                pb_ratio = info['priceToBook']
                if pb_ratio <= 1.5:
                    valuation_score += 5
                elif pb_ratio <= 3.0:
                    valuation_score += 3
            
            if info.get('pegRatio') and info['pegRatio'] > 0:
                peg_ratio = info['pegRatio']
                if peg_ratio <= 1.0:
                    valuation_score += 5
                elif peg_ratio <= 1.5:
                    valuation_score += 2
            
            quality_factors['valuation'] = min(valuation_score, 20)
            max_possible_score += 20
            
            # 4. Growth Assessment (15 points)
            growth_score = 0
            
            if info.get('revenueGrowth') and info['revenueGrowth'] > 0:
                revenue_growth = info['revenueGrowth']
                if revenue_growth >= 0.20:
                    growth_score += 8
                elif revenue_growth >= 0.10:
                    growth_score += 6
                elif revenue_growth >= 0.05:
                    growth_score += 3
            
            if info.get('earningsGrowth') and info['earningsGrowth'] > 0:
                earnings_growth = info['earningsGrowth']
                if earnings_growth >= 0.20:
                    growth_score += 7
                elif earnings_growth >= 0.10:
                    growth_score += 5
                elif earnings_growth >= 0.05:
                    growth_score += 2
            
            quality_factors['growth'] = min(growth_score, 15)
            max_possible_score += 15
            
            # 5. Market Performance Assessment (10 points)
            performance_score = 0
            
            if not hist_data.empty:
                current_price = hist_data['Close'].iloc[-1]
                year_ago_price = hist_data['Close'].iloc[0]
                annual_return = ((current_price - year_ago_price) / year_ago_price) * 100
                
                if annual_return >= 25:
                    performance_score += 6
                elif annual_return >= 15:
                    performance_score += 4
                elif annual_return >= 5:
                    performance_score += 2
                
                # Volatility check
                daily_returns = hist_data['Close'].pct_change().dropna()
                volatility = daily_returns.std() * np.sqrt(252)
                if volatility <= 0.20:
                    performance_score += 4
                elif volatility <= 0.35:
                    performance_score += 2
            
            quality_factors['market_performance'] = min(performance_score, 10)
            max_possible_score += 10
            
            # Calculate final quality score (0-1 scale)
            total_score = sum(quality_factors.values())
            quality_percentage = (total_score / max_possible_score) if max_possible_score > 0 else 0
            
            # Determine quality rating
            if quality_percentage >= 0.85:
                quality_rating = "Excellent Quality"
            elif quality_percentage >= 0.70:
                quality_rating = "High Quality"
            elif quality_percentage >= 0.55:
                quality_rating = "Good Quality"
            elif quality_percentage >= 0.40:
                quality_rating = "Average Quality"
            elif quality_percentage >= 0.25:
                quality_rating = "Below Average"
            else:
                quality_rating = "Poor Quality"
            
            return {
                "quality_score": round(quality_percentage, 3),
                "quality_rating": quality_rating,
                "company_name": company_name,
                "sector": sector,
                "market_cap": market_cap,
                "component_scores": quality_factors,
                "max_possible_score": max_possible_score,
                "detailed_breakdown": {
                    "profitability": f"{quality_factors.get('profitability', 0)}/30",
                    "financial_health": f"{quality_factors.get('financial_health', 0)}/25",
                    "valuation": f"{quality_factors.get('valuation', 0)}/20",
                    "growth": f"{quality_factors.get('growth', 0)}/15",
                    "market_performance": f"{quality_factors.get('market_performance', 0)}/10"
                },
                "assessment_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "quality_score": 0.5,
                "quality_rating": "Assessment Failed",
                "company_name": ticker.replace('.NS', '').replace('.BO', ''),
                "error": str(e),
                "assessment_date": datetime.utcnow().isoformat()
            }

    def _calculate_quality_from_ohlc(self, ticker, ohlc_data):
        """
        Calculate quality score from basic OHLC data when detailed info is not available
        """
        try:
            if not ohlc_data:
                return {
                    "quality_score": 0.5,
                    "quality_rating": "Insufficient Data",
                    "company_name": ticker.replace('.NS', '').replace('.BO', ''),
                    "assessment_date": datetime.utcnow().isoformat()
                }
            
            quality_score = 0.5  # Base score
            
            # Price performance assessment
            price_change = ohlc_data.get('price_change_percent', 0)
            if price_change > 20:
                quality_score += 0.2
            elif price_change > 10:
                quality_score += 0.15
            elif price_change > 0:
                quality_score += 0.1
            elif price_change > -10:
                quality_score += 0.05
            else:
                quality_score -= 0.1
            
            # Volatility assessment
            volatility = ohlc_data.get('volatility', 0.25)
            if volatility <= 0.15:
                quality_score += 0.1
            elif volatility <= 0.25:
                quality_score += 0.05
            elif volatility > 0.4:
                quality_score -= 0.1
            
            # Volume/liquidity assessment
            avg_volume = ohlc_data.get('avg_volume', 0)
            if avg_volume > 5000000:
                quality_score += 0.1
            elif avg_volume > 1000000:
                quality_score += 0.05
            elif avg_volume < 100000:
                quality_score -= 0.05
            
            # Price position relative to 52-week range
            current_price = ohlc_data.get('current_price', 100)
            high_52w = ohlc_data.get('52w_high', 120)
            low_52w = ohlc_data.get('52w_low', 80)
            
            if high_52w > low_52w:
                price_position = (current_price - low_52w) / (high_52w - low_52w)
                if price_position > 0.8:  # Near 52-week high
                    quality_score += 0.05
                elif price_position < 0.2:  # Near 52-week low
                    quality_score -= 0.05
            
            # Clamp score between 0 and 1
            quality_score = max(0, min(1, quality_score))
            
            # Determine rating
            if quality_score >= 0.8:
                quality_rating = "High Quality"
            elif quality_score >= 0.6:
                quality_rating = "Good Quality"
            elif quality_score >= 0.4:
                quality_rating = "Average Quality"
            else:
                quality_rating = "Below Average"
            
            return {
                "quality_score": round(quality_score, 3),
                "quality_rating": quality_rating,
                "company_name": ticker.replace('.NS', '').replace('.BO', ''),
                "data_source": "OHLC Analysis",
                "price_change_percent": price_change,
                "volatility": volatility,
                "assessment_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "quality_score": 0.5,
                "quality_rating": "Assessment Error",
                "company_name": ticker.replace('.NS', '').replace('.BO', ''),
                "error": str(e),
                "assessment_date": datetime.utcnow().isoformat()
            }

    def _generate_portfolio_quality_insights(self, stock_details, quality_distribution):
        """
        Generate insights about the overall quality of stocks in the report
        """
        total_stocks = len(stock_details)
        if total_stocks == 0:
            return {"message": "No stocks to analyze"}
        
        # Calculate quality metrics
        high_quality_count = quality_distribution["High Quality"]
        good_quality_count = quality_distribution["Good Quality"]
        average_quality_count = quality_distribution["Average Quality"]
        below_average_count = quality_distribution["Below Average"]
        
        # Generate insights
        insights = []
        
        # Portfolio quality assessment
        if high_quality_count / total_stocks >= 0.7:
            insights.append("✅ Portfolio consists primarily of high-quality stocks")
        elif (high_quality_count + good_quality_count) / total_stocks >= 0.7:
            insights.append("📈 Portfolio has a good mix of quality stocks")
        elif below_average_count / total_stocks >= 0.5:
            insights.append("⚠️ Portfolio contains significant number of below-average quality stocks")
        else:
            insights.append("📊 Portfolio has mixed quality characteristics")
        
        # Sector diversification insight
        sectors = set()
        for stock_data in stock_details.values():
            if 'sector' in stock_data and stock_data['sector'] != 'Unknown':
                sectors.add(stock_data['sector'])
        
        if len(sectors) >= 3:
            insights.append(f"🌐 Good sector diversification across {len(sectors)} sectors")
        elif len(sectors) == 2:
            insights.append("⚖️ Limited sector diversification")
        else:
            insights.append("🔍 Concentrated in single sector - consider diversification")
        
        # Risk assessment
        high_risk_stocks = []
        for ticker, data in stock_details.items():
            if data.get('quality_score', 0.5) < 0.3:
                high_risk_stocks.append(ticker)
        
        if high_risk_stocks:
            insights.append(f"⚠️ High-risk stocks identified: {', '.join(high_risk_stocks)}")
        
        # Overall recommendation
        avg_quality = sum(data.get('quality_score', 0.5) for data in stock_details.values()) / total_stocks
        if avg_quality >= 0.8:
            overall_recommendation = "Strong portfolio with excellent stock quality"
        elif avg_quality >= 0.65:
            overall_recommendation = "Good portfolio with above-average stock quality"
        elif avg_quality >= 0.5:
            overall_recommendation = "Average portfolio quality - room for improvement"
        else:
            overall_recommendation = "Below-average portfolio quality - consider stock selection review"
        
        return {
            "insights": insights,
            "overall_recommendation": overall_recommendation,
            "average_quality_score": round(avg_quality, 3),
            "sector_count": len(sectors),
            "high_risk_stocks": high_risk_stocks,
            "quality_summary": f"{high_quality_count} high-quality, {good_quality_count} good-quality, {average_quality_count} average, {below_average_count} below-average stocks"
        }

    def calculate_composite_score(self, report_text, analyst="Unknown", tickers=[], plagiarism_score=0.0, ai_probability=0.0):
        """
        Calculate composite quality score for a report (simplified version for quick scoring)
        """
        try:
            # Use the main score_report method with minimal data
            result = self.score_report(
                report_text=report_text,
                analyst=analyst,
                tickers=tickers,
                ohlc_data={},  # Empty OHLC data for quick scoring
                plagiarism_score=plagiarism_score,
                ai_probability=ai_probability
            )
            
            return {
                'composite_score': result.get('composite_quality_score', 0.5),
                'breakdown': {
                    'base_score': result.get('base_composite_score', 0.5),
                    'plagiarism_penalty': result.get('plagiarism_penalty', 0.0),
                    'ai_penalty': result.get('ai_penalty', 0.0),
                    'sebi_compliance': result.get('sebi_compliance', {}).get('score', 0.5),
                    'quality_metrics': result.get('detailed_quality_metrics', {}).get('content_quality_score', 0.5)
                }
            }
        except Exception as e:
            # Fallback to basic scoring if full scoring fails
            return {
                'composite_score': 0.5,
                'breakdown': {
                    'base_score': 0.5,
                    'plagiarism_penalty': 0.0,
                    'ai_penalty': 0.0,
                    'error': str(e)
                }
            }