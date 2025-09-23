# Research Quality Assessment Platform

A comprehensive AI-powered platform for analyzing, scoring, and managing research reports with advanced compliance checking, plagiarism detection, and performance tracking capabilities.

## 🚀 Overview

This platform provides automated quality assessment of research reports using advanced AI models, SEBI compliance checking, plagiarism detection, and comprehensive analytics for analysts and investors.

## 📋 Table of Contents

- [Core Features](#core-features)
- [Dashboard Overview](#dashboard-overview)
- [Analysis Features](#analysis-features)
- [Compliance & Detection](#compliance--detection)
- [User Management](#user-management)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)

## 🎯 Core Features

### 1. **Report Analysis Engine**

- **Automated Quality Scoring**: Composite quality scores based on multiple metrics
- **SEBI Compliance Assessment**: Real-time regulatory compliance checking
- **AI Content Detection**: Identifies AI-generated content with confidence scores
- **Plagiarism Detection**: Advanced similarity detection using BERT embeddings
- **Technical Analysis**: RSI, MACD, and other financial indicators
- **Sentiment Analysis**: News sentiment analysis for mentioned stocks

### 2. **Multi-Dashboard System**

- **Main Dashboard**: Overview of all reports and metrics
- **Investor Dashboard**: Enhanced features for investment analysis
- **Analyst Dashboard**: Personal workspace with assigned topics
- **Admin Dashboard**: Management and oversight capabilities
- **Performance Dashboard**: Individual analyst performance tracking

### 3. **Advanced Analytics**

- **Real-time Metrics**: Live quality and compliance statistics
- **Trending Stocks Backtesting**: 6-month performance analysis
- **Improvement Tracking**: Analyst progress over time
- **Portfolio Analysis**: Comprehensive portfolio commentary generation

## 🏠 Dashboard Overview

### Main Dashboard (`/`)

- **Quick Access Panel**: 4 main feature buttons
- **Reports Leaderboard**: All reports with quality scores
- **Real-time Metrics**: Live performance statistics
- **Quality Trend Charts**: Visual performance tracking
- **Top Analysts Ranking**: Performance-based leaderboard

### Investor Dashboard (`/investor_dashboard`)

- **Real-time SEBI Compliance**: Live compliance assessment
- **Trending Stocks Backtest**: Performance metrics and recommendations
- **Enhanced Analysis Features**: Advanced compliance tools
- **JSON API Integration**: Direct access to report data
- **Quick Actions Panel**: Streamlined workflow tools

### Analyst Dashboard (`/analyst/{name}`)

- **Assigned Topics**: Tasks with deadlines and priorities
- **Progress Tracking**: In-progress and completed work
- **Performance Metrics**: Personal quality statistics
- **Topic Management**: Start/complete task workflow

### Admin Dashboard (`/admin`)

- **Topic Creation**: Assign research tasks to analysts
- **Performance Analytics**: System-wide performance metrics
- **User Management**: Analyst oversight and management
- **System Statistics**: Platform usage and health metrics

## 🔍 Analysis Features

### Report Quality Assessment

- **Factual Accuracy**: Alignment with verified market data
- **Predictive Power**: Future price movement accuracy
- **Bias Detection**: Sentiment vs evidence analysis
- **Originality Score**: Unique insights and content freshness
- **Risk Disclosure**: Comprehensive risk factor coverage
- **Transparency**: Methodology and assumption clarity

### SEBI Compliance Checking

- **Regulatory Requirements**: Automated compliance verification
- **Disclosure Standards**: Mandatory information checking
- **Risk Warnings**: Required risk disclosure validation
- **Registration Verification**: SEBI registration status checking
- **Real-time Assessment**: Live compliance scoring
- **Violation Detection**: Major compliance issue identification

### Technical Analysis Integration

- **Stock Data Integration**: Real-time price and volume data
- **Technical Indicators**: RSI, MACD, moving averages
- **Backtesting Engine**: Historical performance validation
- **Portfolio Metrics**: Risk-adjusted returns and correlations
- **Market Sentiment**: News-based sentiment scoring

## 🛡️ Compliance & Detection

### Plagiarism Detection System

- **BERT Embeddings**: Advanced semantic similarity detection
- **Text Similarity**: TF-IDF based content comparison
- **Segment Matching**: Specific text portion identification
- **Similarity Scoring**: Confidence-based matching scores
- **Historical Comparison**: Cross-reference with existing reports
- **Violation Reporting**: Detailed plagiarism analysis

### AI Content Detection

- **AI Probability Scoring**: Likelihood of AI generation
- **Confidence Metrics**: Detection reliability scores
- **Classification Results**: Human vs AI content categorization
- **Detailed Analysis**: Comprehensive AI detection breakdown
- **Pattern Recognition**: Writing style and structure analysis

### SEBI Compliance Engine

- **Regulatory Framework**: Complete SEBI guideline coverage
- **Automated Checking**: Real-time compliance verification
- **Violation Tracking**: Issue identification and categorization
- **Compliance Scoring**: Percentage-based compliance rating
- **Trend Analysis**: Compliance improvement tracking

## 👥 User Management

### Analyst Profiles (`/analysts`)

- **Profile Creation**: Automatic profile generation
- **Performance Tracking**: Individual analyst metrics
- **Improvement History**: Progress over time visualization
- **Flagged Alerts Tracking**: Issue resolution monitoring
- **Specialization Management**: Expertise area tracking

### Topic Management

- **Admin Assignment**: Task creation and assignment
- **Deadline Tracking**: Due date monitoring and alerts
- **Progress Monitoring**: Task completion tracking
- **Report Linking**: Connect completed tasks to reports
- **Category Organization**: Task categorization system

### Performance Analytics

- **Quality Trends**: Individual and system-wide trends
- **Improvement Scoring**: Quantified progress metrics
- **Comparative Analysis**: Analyst performance comparison
- **Alert Resolution**: Issue fixing progress tracking

## 🔌 API Endpoints

### Report Management

- `POST /analyze` - Submit new report for analysis
- `GET /report/{id}` - View detailed report analysis
- `GET /api/report/{id}/json` - Get report data as JSON
- `GET /report_hub` - Browse all reports
- `GET /compare_reports` - Multi-report comparison tool

### Analytics & Metrics

- `GET /api/metrics` - Real-time platform metrics
- `GET /api/analyst/{name}/improvement_history` - Analyst progress
- `GET /test_analyst_performance` - Available analysts list

### Compliance & Detection

- `GET /api/plagiarism_check/{id}` - Plagiarism results
- `GET /api/ai_detection/{id}` - AI detection results
- `GET /plagiarism_analysis/{id}` - Detailed plagiarism view
- `GET /ai_detection_analysis/{id}` - Detailed AI analysis

### User & Topic Management

- `POST /admin/create_topic` - Create new analyst task
- `POST /api/topic/{id}/start` - Start assigned topic
- `POST /api/topic/{id}/complete` - Complete topic
- `GET /api/admin/topics` - All topics overview

### Portfolio & Market Data

- `POST /analyze_portfolio` - Generate portfolio commentary
- `GET /portfolio` - Portfolio analysis dashboard
- `GET /alerts` - Price and RSI alerts management
- `POST /create_alert` - Create new market alert

## ⚙️ Installation & Setup

### Prerequisites

```bash
Python 3.8+
Flask 2.0+
SQLAlchemy
yfinance
transformers (optional, for BERT)
torch (optional, for BERT)
ollama (for LLM integration)
```

### Installation Steps

```bash
# Clone repository
git clone [repository-url]
cd research-quality-platform

# Install dependencies
pip install -r requirements.txt

# Initialize database
python app.py

# Access application
http://localhost:80
```

### Configuration

- Update `config.py` with your settings
- Configure LLM models in `models/llm_integration.py`
- Set up BERT models for plagiarism detection (optional)
- Configure market data sources

## 📖 Usage Guide

### For Analysts

1. **Access Dashboard**: Visit `/analyst/{your-name}`
2. **View Assigned Topics**: See tasks with deadlines
3. **Submit Reports**: Use "Analyze New Report" feature
4. **Track Performance**: Visit `/analyst/{your-name}/performance`
5. **View Profile**: Check `/analyst/{your-name}/profile`

### For Investors

1. **Access Dashboard**: Visit `/investor_dashboard`
2. **Review Compliance**: Check real-time SEBI compliance
3. **Analyze Trends**: View trending stocks backtesting
4. **Compare Reports**: Use multi-report comparison tool
5. **Access JSON Data**: Use API links for integration

### For Administrators

1. **Access Admin Panel**: Visit `/admin`
2. **Create Topics**: Assign tasks to analysts
3. **Monitor Performance**: Track system-wide metrics
4. **Manage Users**: Oversee analyst performance
5. **View Analytics**: Check `/admin/performance`

## 🔧 Advanced Features

### Real-time Capabilities

- **Live Metrics**: Auto-refreshing dashboard statistics
- **WebSocket Alerts**: Real-time price and RSI notifications
- **Dynamic Compliance**: Continuous SEBI compliance monitoring
- **Performance Tracking**: Live analyst performance updates

### Integration Capabilities

- **JSON API**: Complete report data export
- **AI Knowledge Base**: Structured data for AI systems
- **Market Data Integration**: Real-time stock price feeds
- **News Integration**: Automated news sentiment analysis

### Customization Options

- **Scoring Weights**: Adjustable quality metric weights
- **Compliance Rules**: Customizable SEBI compliance checks
- **Alert Thresholds**: Configurable alert parameters
- **Dashboard Layouts**: Customizable dashboard views

## 📊 Metrics & KPIs

### Quality Metrics

- Composite Quality Score (0-100%)
- SEBI Compliance Score (0-100%)
- Plagiarism Detection Score (0-100%)
- AI Detection Probability (0-100%)

### Performance Metrics

- Analyst Improvement Score
- Report Processing Time
- Compliance Trend Analysis
- Issue Resolution Rate

### System Metrics

- Total Reports Processed
- Active Analysts Count
- Average Quality Score
- Compliance Rate

## 🚨 Alerts & Notifications

### Price Alerts

- Stock price threshold alerts
- RSI overbought/oversold notifications
- Volume spike alerts
- Custom condition alerts

### Quality Alerts

- Low quality score warnings
- Compliance violation alerts
- Plagiarism detection notifications
- AI content detection alerts

## 🔒 Security Features

- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Secure API endpoints
- Data encryption for sensitive information

## 📈 Future Enhancements

- Machine learning model improvements
- Additional compliance frameworks
- Enhanced visualization capabilities
- Mobile application support
- Advanced portfolio optimization tools

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:

- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

---

**Version**: 2.4.1.2
**Last Updated**: 2024
**Platform**: Web-based Flask Application
**Database**: SQLite/PostgreSQL Compatible
