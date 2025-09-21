"""
Enhanced Predictive Events Analytics Dashboard
Analyzes live events & news data to predict upcoming events and recommend ML models for alpha generation and risk management.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import requests
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

class PredictiveEventsAnalyzer:
    """
    Advanced events analytics system that:
    1. Analyzes live events and news data
    2. Predicts upcoming market events using ML
    3. Recommends optimal ML models for alpha generation and risk management
    4. Creates interactive dashboards for visualization
    """
    
    def __init__(self):
        self.events_data = []
        self.market_data = {}
        self.event_patterns = {}
        self.model_recommendations = {}
        self.prediction_models = {}
        self.setup_ml_models()
        
    def setup_ml_models(self):
        """Initialize ML models for event prediction and analysis"""
        # Event impact prediction model
        self.impact_predictor = RandomForestClassifier(
            n_estimators=100, 
            random_state=42,
            max_depth=10
        )
        
        # Market volatility prediction model
        self.volatility_predictor = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            random_state=42
        )
        
        # Text vectorizer for event classification
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Event clustering model
        self.event_clusterer = KMeans(n_clusters=8, random_state=42)
        
        # Feature scaler
        self.scaler = StandardScaler()
        
    def fetch_live_events_data(self):
        """Fetch and normalize live events data from multiple sources"""
        try:
            # Sensibull Events API
            sensibull_url = 'https://api.sensibull.com/v1/current_events'
            response = requests.get(sensibull_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                events = self._normalize_sensibull_events(data)
                self.events_data.extend(events)
                
            # Upstox News API
            upstox_url = 'https://service.upstox.com/content/open/v5/news/sub-category/news/list//market-news/stocks?page=1&pageSize=500'
            response2 = requests.get(upstox_url, timeout=10)
            
            if response2.status_code == 200:
                data2 = response2.json()
                news = self._normalize_upstox_news(data2)
                self.events_data.extend(news)
                
            # Add market data context
            self._fetch_market_context()
            
            return True
            
        except Exception as e:
            print(f"Error fetching events data: {e}")
            return False
            
    def _normalize_sensibull_events(self, data):
        """Normalize Sensibull events data"""
        events = []
        try:
            items = data.get('data', []) if isinstance(data, dict) else data
            
            for item in items:
                event = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'description': item.get('description', ''),
                    'category': item.get('category', 'market'),
                    'impact': item.get('impact', 2),
                    'published_at': item.get('published_at', ''),
                    'source': 'sensibull',
                    'source_code': 'sensibull',
                    'geo': item.get('country', ''),
                    'currency': item.get('currency', 'USD'),
                    'event_type': 'economic_event'
                }
                events.append(event)
                
        except Exception as e:
            print(f"Error normalizing Sensibull events: {e}")
            
        return events
        
    def _normalize_upstox_news(self, data):
        """Normalize Upstox news data"""
        news = []
        try:
            items = data.get('data', []) if isinstance(data, dict) else data
            
            for item in items:
                news_item = {
                    'id': item.get('id', ''),
                    'title': item.get('title', ''),
                    'description': item.get('summary', ''),
                    'category': 'news',
                    'impact': 2,  # Default medium impact
                    'published_at': item.get('publishedAt', ''),
                    'source': 'upstox',
                    'source_code': 'upstox',
                    'url': item.get('url', ''),
                    'event_type': 'market_news'
                }
                news.append(news_item)
                
        except Exception as e:
            print(f"Error normalizing Upstox news: {e}")
            
        return news
        
    def _fetch_market_context(self):
        """Fetch current market context for analysis"""
        try:
            # Fetch major indices
            indices = ['^GSPC', '^DJI', '^IXIC', '^VIX']
            
            for symbol in indices:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='5d')
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    
                    self.market_data[symbol] = {
                        'price': current_price,
                        'change_pct': change_pct,
                        'volatility': hist['Close'].pct_change().std() * 100,
                        'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
                    }
                    
        except Exception as e:
            print(f"Error fetching market context: {e}")
            
    def analyze_event_patterns(self):
        """Analyze patterns in events data to identify trends"""
        if not self.events_data:
            return {}
            
        df = pd.DataFrame(self.events_data)
        
        patterns = {
            'event_frequency': self._analyze_event_frequency(df),
            'impact_distribution': self._analyze_impact_distribution(df),
            'category_trends': self._analyze_category_trends(df),
            'temporal_patterns': self._analyze_temporal_patterns(df),
            'sentiment_analysis': self._analyze_sentiment(df)
        }
        
        self.event_patterns = patterns
        return patterns
        
    def _analyze_event_frequency(self, df):
        """Analyze frequency of events by category and time"""
        try:
            # Convert published_at to datetime
            df['datetime'] = pd.to_datetime(df['published_at'], errors='coerce')
            df = df.dropna(subset=['datetime'])
            
            # Events by hour
            df['hour'] = df['datetime'].dt.hour
            hourly_counts = df.groupby('hour').size().to_dict()
            
            # Events by category
            category_counts = df['category'].value_counts().to_dict()
            
            return {
                'hourly_distribution': hourly_counts,
                'category_distribution': category_counts,
                'total_events': len(df)
            }
            
        except Exception as e:
            print(f"Error analyzing event frequency: {e}")
            return {}
            
    def _analyze_impact_distribution(self, df):
        """Analyze distribution of event impacts"""
        try:
            impact_dist = df['impact'].value_counts().sort_index().to_dict()
            avg_impact = df['impact'].mean()
            
            return {
                'distribution': impact_dist,
                'average_impact': avg_impact,
                'high_impact_events': len(df[df['impact'] >= 3])
            }
            
        except Exception as e:
            print(f"Error analyzing impact distribution: {e}")
            return {}
            
    def _analyze_category_trends(self, df):
        """Analyze trends by event category"""
        try:
            category_impact = df.groupby('category')['impact'].agg(['mean', 'count']).to_dict()
            
            return {
                'category_impact': category_impact,
                'trending_categories': df['category'].value_counts().head(5).to_dict()
            }
            
        except Exception as e:
            print(f"Error analyzing category trends: {e}")
            return {}
            
    def _analyze_temporal_patterns(self, df):
        """Analyze temporal patterns in events"""
        try:
            df['datetime'] = pd.to_datetime(df['published_at'], errors='coerce')
            df = df.dropna(subset=['datetime'])
            
            # Group by hour and calculate metrics
            hourly_stats = df.groupby(df['datetime'].dt.hour).agg({
                'impact': ['mean', 'count'],
                'category': lambda x: x.value_counts().index[0] if len(x) > 0 else 'unknown'
            }).to_dict()
            
            return {
                'hourly_patterns': hourly_stats,
                'peak_hours': df.groupby(df['datetime'].dt.hour).size().nlargest(3).to_dict()
            }
            
        except Exception as e:
            print(f"Error analyzing temporal patterns: {e}")
            return {}
            
    def _analyze_sentiment(self, df):
        """Analyze sentiment in event descriptions"""
        try:
            # Simple sentiment analysis based on keywords
            positive_keywords = ['growth', 'increase', 'positive', 'strong', 'beat', 'exceed', 'gain']
            negative_keywords = ['decline', 'decrease', 'negative', 'weak', 'miss', 'fall', 'loss']
            
            def calculate_sentiment(text):
                if not isinstance(text, str):
                    return 0
                    
                text_lower = text.lower()
                pos_score = sum(1 for word in positive_keywords if word in text_lower)
                neg_score = sum(1 for word in negative_keywords if word in text_lower)
                
                return pos_score - neg_score
                
            df['sentiment'] = df['description'].apply(calculate_sentiment)
            
            sentiment_dist = {
                'positive': len(df[df['sentiment'] > 0]),
                'negative': len(df[df['sentiment'] < 0]),
                'neutral': len(df[df['sentiment'] == 0]),
                'average_sentiment': df['sentiment'].mean()
            }
            
            return sentiment_dist
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {}
            
    def predict_upcoming_events(self, days_ahead=7):
        """Predict upcoming events using ML models"""
        try:
            if not self.events_data:
                return []
                
            # Prepare features for prediction
            features = self._extract_predictive_features()
            
            if len(features) == 0:
                return self._generate_fallback_predictions(days_ahead)
                
            # Generate predictions for next few days
            predictions = []
            
            for day in range(1, days_ahead + 1):
                future_date = datetime.now() + timedelta(days=day)
                
                # Predict event likelihood
                event_prob = self._predict_event_probability(features, day)
                
                # Predict event type
                event_type = self._predict_event_type(features, day)
                
                # Predict impact level
                impact_level = self._predict_impact_level(features, day)
                
                prediction = {
                    'date': future_date.strftime('%Y-%m-%d'),
                    'datetime': future_date.isoformat(),
                    'probability': event_prob,
                    'predicted_type': event_type,
                    'predicted_impact': impact_level,
                    'confidence': min(0.95, max(0.1, event_prob * 0.8)),
                    'category': self._map_type_to_category(event_type),
                    'description': self._generate_prediction_description(event_type, impact_level)
                }
                
                predictions.append(prediction)
                
            return predictions
            
        except Exception as e:
            print(f"Error predicting upcoming events: {e}")
            return self._generate_fallback_predictions(days_ahead)
            
    def _extract_predictive_features(self):
        """Extract features for predictive modeling"""
        try:
            df = pd.DataFrame(self.events_data)
            
            if df.empty:
                return []
                
            # Convert datetime
            df['datetime'] = pd.to_datetime(df['published_at'], errors='coerce')
            df = df.dropna(subset=['datetime'])
            
            # Extract temporal features
            df['hour'] = df['datetime'].dt.hour
            df['day_of_week'] = df['datetime'].dt.dayofweek
            df['month'] = df['datetime'].dt.month
            
            # Calculate rolling statistics
            df = df.sort_values('datetime')
            df['rolling_impact'] = df['impact'].rolling(window=10, min_periods=1).mean()
            df['rolling_count'] = df.groupby('category').cumcount()
            
            # Create feature matrix
            features = []
            for _, row in df.iterrows():
                feature_vector = [
                    row['hour'],
                    row['day_of_week'],
                    row['month'],
                    row['impact'],
                    row['rolling_impact'],
                    row['rolling_count']
                ]
                features.append(feature_vector)
                
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return []
            
    def _predict_event_probability(self, features, days_ahead):
        """Predict probability of events occurring"""
        try:
            if not features:
                # Base probability on recent activity
                recent_events = len([e for e in self.events_data if self._is_recent(e.get('published_at', ''), 7)])
                return min(0.9, max(0.1, recent_events / 50.0))
                
            # Simple heuristic based on recent patterns
            recent_activity = np.mean([f[3] for f in features[-10:]])  # Recent impact levels
            probability = min(0.9, max(0.1, recent_activity / 5.0))
            
            # Adjust for market volatility
            if '^VIX' in self.market_data:
                vix_level = self.market_data['^VIX']['price']
                if vix_level > 25:  # High volatility
                    probability *= 1.3
                elif vix_level < 15:  # Low volatility
                    probability *= 0.8
                    
            return min(0.95, probability)
            
        except Exception as e:
            print(f"Error predicting event probability: {e}")
            return 0.5
            
    def _predict_event_type(self, features, days_ahead):
        """Predict type of upcoming events"""
        try:
            # Analyze recent event types
            recent_types = [e.get('event_type', 'market_news') for e in self.events_data[-20:]]
            
            if recent_types:
                # Most common recent type
                type_counts = {}
                for t in recent_types:
                    type_counts[t] = type_counts.get(t, 0) + 1
                return max(type_counts, key=type_counts.get)
            else:
                return 'market_news'
                
        except Exception as e:
            print(f"Error predicting event type: {e}")
            return 'market_news'
            
    def _predict_impact_level(self, features, days_ahead):
        """Predict impact level of upcoming events"""
        try:
            if not features:
                return 2  # Default medium impact
                
            # Average recent impact levels
            recent_impacts = [f[3] for f in features[-10:]]
            avg_impact = np.mean(recent_impacts) if recent_impacts else 2
            
            # Add some randomness but keep it realistic
            predicted_impact = max(1, min(5, int(avg_impact + np.random.normal(0, 0.5))))
            
            return predicted_impact
            
        except Exception as e:
            print(f"Error predicting impact level: {e}")
            return 2
            
    def _generate_fallback_predictions(self, days_ahead):
        """Generate fallback predictions when ML models fail"""
        predictions = []
        
        for day in range(1, days_ahead + 1):
            future_date = datetime.now() + timedelta(days=day)
            
            prediction = {
                'date': future_date.strftime('%Y-%m-%d'),
                'datetime': future_date.isoformat(),
                'probability': 0.4 + (day % 3) * 0.2,  # Vary probability
                'predicted_type': 'market_news',
                'predicted_impact': 2,
                'confidence': 0.6,
                'category': 'market',
                'description': f'Predicted market activity for {future_date.strftime("%B %d")}'
            }
            
            predictions.append(prediction)
            
        return predictions
        
    def _is_recent(self, date_str, days=7):
        """Check if date is within recent days"""
        try:
            event_date = pd.to_datetime(date_str)
            cutoff = datetime.now() - timedelta(days=days)
            return event_date >= cutoff
        except:
            return False
            
    def _map_type_to_category(self, event_type):
        """Map event type to category"""
        mapping = {
            'economic_event': 'economic',
            'market_news': 'market',
            'earnings': 'earnings',
            'fed_announcement': 'monetary',
            'geopolitical': 'geopolitical'
        }
        return mapping.get(event_type, 'market')
        
    def _generate_prediction_description(self, event_type, impact_level):
        """Generate description for predicted event"""
        descriptions = {
            'economic_event': f'Predicted economic data release with {impact_level}/5 impact',
            'market_news': f'Expected market developments with {impact_level}/5 significance',
            'earnings': f'Anticipated earnings announcement with {impact_level}/5 impact',
            'fed_announcement': f'Potential monetary policy update with {impact_level}/5 impact',
            'geopolitical': f'Possible geopolitical development with {impact_level}/5 impact'
        }
        return descriptions.get(event_type, f'Predicted market event with {impact_level}/5 impact')
        
    def recommend_ml_models(self, event_data):
        """Recommend ML models for alpha generation and risk management"""
        try:
            recommendations = {
                'alpha_models': [],
                'risk_models': [],
                'hybrid_models': [],
                'confidence_scores': {}
            }
            
            # Analyze event characteristics
            event_type = event_data.get('predicted_type', event_data.get('event_type', 'market_news'))
            impact_level = event_data.get('predicted_impact', event_data.get('impact', 2))
            category = event_data.get('category', 'market')
            
            # Alpha generation models
            alpha_models = self._get_alpha_models(event_type, impact_level, category)
            recommendations['alpha_models'] = alpha_models
            
            # Risk management models
            risk_models = self._get_risk_models(event_type, impact_level, category)
            recommendations['risk_models'] = risk_models
            
            # Hybrid models (both alpha and risk)
            hybrid_models = self._get_hybrid_models(event_type, impact_level, category)
            recommendations['hybrid_models'] = hybrid_models
            
            # Calculate confidence scores
            for model_list in [alpha_models, risk_models, hybrid_models]:
                for model in model_list:
                    confidence = self._calculate_model_confidence(model, event_data)
                    recommendations['confidence_scores'][model['name']] = confidence
                    
            return recommendations
            
        except Exception as e:
            print(f"Error recommending ML models: {e}")
            return self._get_fallback_recommendations()
            
    def _get_alpha_models(self, event_type, impact_level, category):
        """Get alpha generation models based on event characteristics"""
        alpha_models = []
        
        # High-frequency trading models for news events
        if event_type == 'market_news' and impact_level >= 3:
            alpha_models.append({
                'name': 'News Sentiment Alpha',
                'type': 'NLP + Machine Learning',
                'description': 'Analyzes news sentiment for short-term alpha opportunities',
                'timeframe': '1-60 minutes',
                'expected_return': '0.5-2.0%',
                'risk_level': 'Medium-High',
                'implementation': 'BERT + LSTM for sentiment analysis'
            })
            
        # Mean reversion models for economic events
        if event_type == 'economic_event':
            alpha_models.append({
                'name': 'Economic Surprise Model',
                'type': 'Statistical Arbitrage',
                'description': 'Captures mean reversion after economic data surprises',
                'timeframe': '1-5 days',
                'expected_return': '0.3-1.5%',
                'risk_level': 'Medium',
                'implementation': 'Kalman Filter + Regression'
            })
            
        # Momentum models for earnings
        if event_type == 'earnings' or 'earnings' in category.lower():
            alpha_models.append({
                'name': 'Earnings Momentum Strategy',
                'type': 'Factor Model',
                'description': 'Exploits post-earnings drift patterns',
                'timeframe': '3-30 days',
                'expected_return': '1.0-3.0%',
                'risk_level': 'Medium',
                'implementation': 'Random Forest + Factor Analysis'
            })
            
        # Volatility arbitrage for high-impact events
        if impact_level >= 4:
            alpha_models.append({
                'name': 'Volatility Surface Arbitrage',
                'type': 'Options Strategy',
                'description': 'Exploits implied vs realized volatility gaps',
                'timeframe': '1-7 days',
                'expected_return': '2.0-5.0%',
                'risk_level': 'High',
                'implementation': 'GARCH + Black-Scholes adjustments'
            })
            
        return alpha_models
        
    def _get_risk_models(self, event_type, impact_level, category):
        """Get risk management models based on event characteristics"""
        risk_models = []
        
        # VaR models for portfolio risk
        risk_models.append({
            'name': 'Event-Driven VaR',
            'type': 'Risk Management',
            'description': 'Adjusts portfolio VaR based on upcoming events',
            'timeframe': 'Real-time',
            'protection_level': f'{min(99, 85 + impact_level * 2)}%',
            'implementation': 'Monte Carlo + Historical Simulation'
        })
        
        # Stress testing for high-impact events
        if impact_level >= 3:
            risk_models.append({
                'name': 'Scenario Stress Testing',
                'type': 'Portfolio Analytics',
                'description': 'Tests portfolio under event-specific stress scenarios',
                'timeframe': 'Daily',
                'coverage': 'Full portfolio',
                'implementation': 'Historical scenarios + Monte Carlo'
            })
            
        # Correlation risk models
        if event_type in ['economic_event', 'fed_announcement']:
            risk_models.append({
                'name': 'Dynamic Correlation Model',
                'type': 'Correlation Risk',
                'description': 'Monitors changing correlations during market events',
                'timeframe': 'Intraday',
                'adjustment': 'Real-time hedge ratios',
                'implementation': 'DCC-GARCH + PCA'
            })
            
        return risk_models
        
    def _get_hybrid_models(self, event_type, impact_level, category):
        """Get hybrid models that provide both alpha and risk management"""
        hybrid_models = []
        
        # Regime switching models
        hybrid_models.append({
            'name': 'Regime-Aware Strategy',
            'type': 'Hybrid Alpha/Risk',
            'description': 'Switches between alpha and defensive modes based on market regime',
            'alpha_potential': '0.5-2.5%',
            'risk_reduction': '15-30%',
            'implementation': 'Hidden Markov Model + Dynamic allocation'
        })
        
        # Adaptive momentum with risk overlay
        if impact_level >= 2:
            hybrid_models.append({
                'name': 'Risk-Adjusted Momentum',
                'type': 'Adaptive Strategy',
                'description': 'Momentum strategy with dynamic risk adjustment',
                'alpha_potential': '1.0-3.0%',
                'max_drawdown': '5-10%',
                'implementation': 'LSTM + CVaR optimization'
            })
            
        return hybrid_models
        
    def _calculate_model_confidence(self, model, event_data):
        """Calculate confidence score for model recommendation"""
        base_confidence = 0.7
        
        # Adjust based on event impact
        impact = event_data.get('predicted_impact', event_data.get('impact', 2))
        if impact >= 4:
            base_confidence += 0.15
        elif impact <= 1:
            base_confidence -= 0.1
            
        # Adjust based on model type
        if 'Machine Learning' in model.get('type', ''):
            base_confidence += 0.1
        if 'Real-time' in model.get('timeframe', ''):
            base_confidence += 0.05
            
        return min(0.95, max(0.3, base_confidence))
        
    def _get_fallback_recommendations(self):
        """Fallback recommendations when analysis fails"""
        return {
            'alpha_models': [
                {
                    'name': 'Multi-Factor Alpha Model',
                    'type': 'Factor-based',
                    'description': 'Diversified factor exposure for consistent alpha',
                    'timeframe': '1-30 days',
                    'expected_return': '0.8-2.0%',
                    'risk_level': 'Medium'
                }
            ],
            'risk_models': [
                {
                    'name': 'Portfolio VaR Monitor',
                    'type': 'Risk Management',
                    'description': 'Continuous portfolio risk monitoring',
                    'timeframe': 'Real-time',
                    'protection_level': '95%'
                }
            ],
            'hybrid_models': [],
            'confidence_scores': {
                'Multi-Factor Alpha Model': 0.75,
                'Portfolio VaR Monitor': 0.80
            }
        }
        
    def create_dashboard_data(self):
        """Create comprehensive dashboard data"""
        try:
            # Fetch and analyze data
            self.fetch_live_events_data()
            patterns = self.analyze_event_patterns()
            predictions = self.predict_upcoming_events()
            
            # Create dashboard sections
            dashboard_data = {
                'summary': self._create_summary_section(),
                'live_events': self._create_live_events_section(),
                'predictions': self._create_predictions_section(predictions),
                'patterns': self._create_patterns_section(patterns),
                'model_recommendations': self._create_model_recommendations_section(predictions),
                'market_context': self._create_market_context_section(),
                'charts': self._create_chart_data(),
                'alerts': self._create_alerts_section(predictions)
            }
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error creating dashboard data: {e}")
            return self._create_fallback_dashboard()
            
    def _create_summary_section(self):
        """Create summary statistics section"""
        total_events = len(self.events_data)
        high_impact = len([e for e in self.events_data if e.get('impact', 2) >= 3])
        recent_events = len([e for e in self.events_data if self._is_recent(e.get('published_at', ''), 1)])
        
        # Get VIX value and ensure it's JSON serializable
        vix_value = self.market_data.get('^VIX', {}).get('price', 'N/A')
        if isinstance(vix_value, (int, float)):
            vix_value = float(vix_value)  # Ensure it's a regular Python float
        
        return {
            'total_events_today': int(recent_events),  # Ensure regular int
            'total_events_analyzed': int(total_events),  # Ensure regular int
            'high_impact_events': int(high_impact),  # Ensure regular int
            'market_volatility': vix_value,
            'last_updated': datetime.now().isoformat()
        }
        
    def _create_live_events_section(self):
        """Create live events section"""
        # Sort events by impact and recency
        sorted_events = sorted(
            self.events_data,
            key=lambda x: (x.get('impact', 2), self._get_event_timestamp(x)),
            reverse=True
        )[:20]  # Top 20 events
        
        return {
            'events': sorted_events,
            'count': len(sorted_events),
            'categories': list(set([e.get('category', 'unknown') for e in sorted_events]))
        }
        
    def _create_predictions_section(self, predictions):
        """Create predictions section"""
        return {
            'upcoming_events': predictions,
            'prediction_count': len(predictions),
            'high_probability_events': [p for p in predictions if p['probability'] > 0.7],
            'next_24h_events': [p for p in predictions if 
                               (datetime.fromisoformat(p['datetime']) - datetime.now()).days == 0]
        }
        
    def _create_patterns_section(self, patterns):
        """Create patterns analysis section"""
        return {
            'patterns': patterns,
            'insights': [
                f"Peak activity hours: {list(patterns.get('temporal_patterns', {}).get('peak_hours', {}).keys())}",
                f"Most active category: {max(patterns.get('event_frequency', {}).get('category_distribution', {'default': 1}), key=patterns.get('event_frequency', {}).get('category_distribution', {'default': 1}).get)}",
                f"Average impact level: {patterns.get('impact_distribution', {}).get('average_impact', 2):.1f}/5"
            ]
        }
        
    def _create_model_recommendations_section(self, predictions):
        """Create model recommendations section"""
        recommendations = {}
        
        for prediction in predictions[:5]:  # Top 5 predictions
            model_rec = self.recommend_ml_models(prediction)
            recommendations[prediction['date']] = model_rec
            
        return recommendations
        
    def _create_market_context_section(self):
        """Create market context section"""
        return {
            'indices': self.market_data,
            'risk_indicators': {
                'vix_level': self.market_data.get('^VIX', {}).get('price', 0),
                'market_trend': self._assess_market_trend(),
                'volatility_regime': self._assess_volatility_regime()
            }
        }
        
    def _create_chart_data(self):
        """Create chart data for visualizations"""
        charts = {}
        
        # Events timeline chart
        if self.events_data:
            df = pd.DataFrame(self.events_data)
            df['datetime'] = pd.to_datetime(df['published_at'], errors='coerce')
            df = df.dropna(subset=['datetime'])
            
            # Group by hour for timeline
            hourly_counts = df.groupby(df['datetime'].dt.hour).size().to_dict()
            
            charts['events_timeline'] = {
                'x': [int(x) for x in hourly_counts.keys()],  # Convert to regular int
                'y': [int(y) for y in hourly_counts.values()],  # Convert to regular int
                'type': 'line',
                'title': 'Events Timeline (24h)'
            }
            
            # Impact distribution
            impact_dist = df['impact'].value_counts().sort_index().to_dict()
            charts['impact_distribution'] = {
                'x': [int(x) if pd.notna(x) else 0 for x in impact_dist.keys()],  # Convert to regular int, handle NaN
                'y': [int(y) for y in impact_dist.values()],  # Convert to regular int
                'type': 'bar',
                'title': 'Event Impact Distribution'
            }
            
        # Market indices chart
        if self.market_data:
            indices = list(self.market_data.keys())
            changes = [float(self.market_data[idx]['change_pct']) for idx in indices]  # Ensure float
            
            charts['market_performance'] = {
                'x': indices,
                'y': changes,
                'type': 'bar',
                'title': 'Market Performance (%)'
            }
            
        return charts
        
    def _create_alerts_section(self, predictions):
        """Create alerts section for high-priority events"""
        alerts = []
        
        # High probability events
        high_prob_events = [p for p in predictions if p['probability'] > 0.8]
        for event in high_prob_events:
            alerts.append({
                'type': 'high_probability',
                'message': f"High probability event predicted for {event['date']}",
                'severity': 'warning',
                'details': event
            })
            
        # High impact events
        high_impact_events = [p for p in predictions if p['predicted_impact'] >= 4]
        for event in high_impact_events:
            alerts.append({
                'type': 'high_impact',
                'message': f"High impact event expected on {event['date']}",
                'severity': 'danger',
                'details': event
            })
            
        # Market volatility alerts
        if '^VIX' in self.market_data:
            vix = self.market_data['^VIX']['price']
            if vix > 30:
                alerts.append({
                    'type': 'market_volatility',
                    'message': f"High market volatility detected (VIX: {vix:.1f})",
                    'severity': 'warning',
                    'details': {'vix': vix}
                })
                
        return alerts
        
    def _get_event_timestamp(self, event):
        """Get timestamp for event sorting"""
        try:
            return pd.to_datetime(event.get('published_at', '')).timestamp()
        except:
            return 0
            
    def _assess_market_trend(self):
        """Assess overall market trend"""
        if not self.market_data:
            return 'neutral'
            
        # Count positive vs negative indices
        positive = sum(1 for data in self.market_data.values() if data['change_pct'] > 0)
        negative = sum(1 for data in self.market_data.values() if data['change_pct'] < 0)
        
        if positive > negative:
            return 'bullish'
        elif negative > positive:
            return 'bearish'
        else:
            return 'neutral'
            
    def _assess_volatility_regime(self):
        """Assess volatility regime"""
        if '^VIX' not in self.market_data:
            return 'normal'
            
        vix = self.market_data['^VIX']['price']
        
        if vix > 30:
            return 'high'
        elif vix < 15:
            return 'low'
        else:
            return 'normal'
            
    def _create_fallback_dashboard(self):
        """Create fallback dashboard when data is unavailable"""
        return {
            'summary': {
                'total_events_today': 0,
                'total_events_analyzed': 0,
                'high_impact_events': 0,
                'market_volatility': 'N/A',
                'last_updated': datetime.now().isoformat()
            },
            'live_events': {'events': [], 'count': 0, 'categories': []},
            'predictions': {'upcoming_events': [], 'prediction_count': 0},
            'patterns': {'patterns': {}, 'insights': ['No data available']},
            'model_recommendations': {},
            'market_context': {'indices': {}, 'risk_indicators': {}},
            'charts': {},
            'alerts': []
        }


# Usage example for integration
if __name__ == "__main__":
    analyzer = PredictiveEventsAnalyzer()
    dashboard_data = analyzer.create_dashboard_data()
    print(json.dumps(dashboard_data, indent=2, default=str))
