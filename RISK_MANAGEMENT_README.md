# 🤖 Agentic AI Risk Management System for Investors

## 🎯 Overview

This is a comprehensive **AWS Bedrock-powered agentic AI risk management system** designed specifically for investors. It provides real-time portfolio risk monitoring, stress testing, compliance checking, and intelligent investment guidance through multiple specialized AI agents.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VS Terminal AClass Dashboard                  │
│                   http://127.0.0.1:5008/vs_terminal_AClass      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                Risk Management Dashboard                         │
│      http://127.0.0.1:5008/vs_terminal_AClass/risk_management   │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                  AI Agent Orchestrator                          │
├─────────────────────┼───────────────────────────────────────────┤
│ Risk Monitoring     │ Scenario Simulation │ Compliance Checking │
│ Agent               │ Agent               │ Agent               │
├─────────────────────┼───────────────────────────────────────────┤
│ Advisor Copilot     │ Trade Execution     │ Market Data         │
│ Agent               │ Agent               │ Provider            │
└─────────────────────┼───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│                    AWS Bedrock                                  │
│              (Mistral, Anthropic, etc.)                        │
└─────────────────────────────────────────────────────────────────┘
```

## 🤖 AI Agents

### 1. **Risk Monitoring & Insights Agent**
- **Purpose**: Continuous portfolio risk monitoring
- **Capabilities**:
  - Concentration risk detection
  - Volatility risk assessment
  - Correlation risk analysis
  - Drawdown risk monitoring
- **Triggers**: Real-time price updates, portfolio changes
- **Output**: Risk alerts with actionable recommendations

### 2. **Scenario Simulation Agent**
- **Purpose**: Stress testing and scenario analysis
- **Capabilities**:
  - Market crash scenarios (-30%)
  - Interest rate shock (+200 bps)
  - Sector rotation analysis
  - Currency devaluation impact
- **Triggers**: Scheduled runs, user requests
- **Output**: Comprehensive stress test reports

### 3. **Automated Compliance & Reporting Agent**
- **Purpose**: Regulatory compliance monitoring
- **Capabilities**:
  - Position size limit checks
  - Sector exposure monitoring
  - Regulatory requirement verification
  - Risk tolerance alignment
- **Triggers**: Portfolio changes, scheduled checks
- **Output**: Compliance reports and violation alerts

### 4. **Advisor Copilot Agent**
- **Purpose**: AI-powered investment guidance
- **Capabilities**:
  - Natural language query processing
  - Personalized investment recommendations
  - Risk assessment for strategies
  - Implementation step guidance
- **Triggers**: User queries
- **Output**: Contextual investment advice

### 5. **Trade Execution & Rebalancing Agent**
- **Purpose**: Portfolio optimization suggestions
- **Capabilities**:
  - Current allocation analysis
  - Target allocation calculation
  - Rebalancing trade suggestions
  - Transaction cost estimation
- **Triggers**: Portfolio drift, user requests
- **Output**: Specific trade recommendations

## 📁 File Structure

```
📂 Risk Management System
├── 📄 risk_management_agents.py      # Core AI agents implementation
├── 📄 risk_management_routes.py      # Flask API routes
├── 📄 setup_risk_management.py      # Setup and configuration script
├── 📄 test_risk_management.py       # Comprehensive test suite
├── 📄 app.py                        # Main Flask application (updated)
├── 📂 templates/
│   └── 📄 risk_management_dashboard.html  # Web dashboard UI
├── 📄 README.md                     # This documentation
└── 📄 risk_management_config.json   # Configuration file (created by setup)
```

## 🚀 Quick Start

### 1. **Setup & Installation**
```bash
# Run the setup script
python setup_risk_management.py

# Or install manually:
pip install boto3 yfinance numpy pandas scikit-learn
```

### 2. **Configure AWS Bedrock**
```bash
# Option 1: AWS CLI (Recommended)
aws configure

# Option 2: Environment Variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. **Test the System**
```bash
python test_risk_management.py
```

### 4. **Start the Application**
```bash
python app.py
```

### 5. **Access the Dashboard**
- Main Terminal: http://127.0.0.1:5008/vs_terminal_AClass
- Risk Management: http://127.0.0.1:5008/vs_terminal_AClass/risk_management

## 🔧 API Endpoints

### Core Risk Management APIs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/vs_terminal_AClass/risk_management/comprehensive_analysis` | POST | Run full portfolio risk analysis |
| `/api/vs_terminal_AClass/risk_management/risk_alerts` | GET | Get current risk alerts |
| `/api/vs_terminal_AClass/risk_management/stress_test` | POST | Run stress test scenarios |
| `/api/vs_terminal_AClass/risk_management/compliance_check` | POST | Check compliance status |
| `/api/vs_terminal_AClass/risk_management/advisor_query` | POST | Query AI advisor |
| `/api/vs_terminal_AClass/risk_management/rebalancing_suggestions` | POST | Get rebalancing recommendations |
| `/api/vs_terminal_AClass/risk_management/portfolio_risk_score` | GET | Get current risk score |
| `/api/vs_terminal_AClass/risk_management/risk_heatmap` | GET | Get risk heatmap data |
| `/api/vs_terminal_AClass/risk_management/agent_status` | GET | Get AI agent status |

### Sample API Usage

#### Comprehensive Risk Analysis
```bash
curl -X POST http://127.0.0.1:5008/api/vs_terminal_AClass/risk_management/comprehensive_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "investor_id": "demo_investor",
    "risk_tolerance": "Moderate",
    "portfolio_value": 500000
  }'
```

#### Query AI Advisor
```bash
curl -X POST http://127.0.0.1:5008/api/vs_terminal_AClass/risk_management/advisor_query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Should I increase my IT sector exposure?",
    "investor_id": "demo_investor",
    "risk_tolerance": "Moderate"
  }'
```

## 🎨 Dashboard Features

### Real-time Risk Monitoring
- **Overall Risk Score**: 0-10 scale with visual risk meter
- **Live Agent Status**: Real-time monitoring of all AI agents
- **Active Alerts**: Priority-based risk alert system
- **Compliance Score**: Regulatory compliance percentage

### Interactive Analytics
- **Risk Heatmap**: Visual representation of sector and stock risks
- **Portfolio Allocation**: Interactive pie chart of current allocation
- **Stress Test Results**: Comprehensive scenario analysis results
- **Performance Metrics**: Historical agent performance tracking

### AI Advisor Chat
- **Natural Language Interface**: Ask questions in plain English
- **Contextual Responses**: Answers based on your specific portfolio
- **Implementation Guidance**: Step-by-step action plans
- **Risk Assessment**: Risk scoring for all recommendations

## ⚙️ Configuration

### Risk Thresholds (risk_management_config.json)
```json
{
  "risk_management": {
    "risk_thresholds": {
      "concentration_limit": 0.15,      // Max 15% in single position
      "sector_limit": 0.4,              // Max 40% in single sector
      "volatility_threshold": 25.0,     // VIX threshold for alerts
      "drawdown_threshold": -15.0       // Max acceptable drawdown
    }
  }
}
```

### Agent Settings
```json
{
  "agent_settings": {
    "risk_monitoring_agent": {
      "enabled": true,
      "confidence_threshold": 0.8
    },
    "scenario_simulation_agent": {
      "enabled": true,
      "scenarios": "all"
    }
  }
}
```

## 🔄 Development vs Production

### Testing Environment (Current)
- **Database**: SQLite with demo data
- **Market Data**: YFinance API
- **AI Models**: AWS Bedrock with fallback responses
- **Authentication**: Demo investor session
- **Data**: Mock portfolio and market data

### Production Environment (Ready)
- **Database**: AWS RDS with live investor data
- **Market Data**: Fyers API with real-time feeds
- **AI Models**: Full AWS Bedrock integration
- **Authentication**: Full investor authentication system
- **Data**: Live market data and real portfolios

### Migration Path
1. Set up AWS RDS database
2. Configure Fyers API credentials
3. Update database connection strings
4. Deploy to AWS EC2/ECS
5. Configure production environment variables

## 🛡️ Security & Compliance

### Data Security
- **AWS IAM**: Role-based access control for Bedrock
- **Encryption**: All data encrypted in transit and at rest
- **Session Management**: Secure session handling
- **API Rate Limiting**: Protection against abuse

### Compliance Features
- **SEBI Compliance**: Built-in Indian regulatory checks
- **Position Limits**: Automated position size monitoring
- **Risk Tolerance**: Alignment with investor risk profiles
- **Audit Trail**: Complete logging of all AI decisions

## 🔍 Monitoring & Debugging

### System Health Monitoring
```python
# Check agent status
GET /api/vs_terminal_AClass/risk_management/agent_status

# Monitor system health
- Agent uptime and performance
- AWS Bedrock API status
- Database connection status
- Market data feed status
```

### Debugging Tools
- **Comprehensive test suite**: `test_risk_management.py`
- **Detailed logging**: All agent actions logged
- **Fallback responses**: System works even when external services fail
- **Error handling**: Graceful degradation of features

## 📈 Sample Use Cases

### 1. Daily Risk Monitoring
```python
# Automated daily risk check
analysis = await orchestrator.run_comprehensive_risk_analysis(investor_profile)
if analysis['overall_risk_score'] > 8.0:
    send_high_risk_alert()
```

### 2. Investment Decision Support
```
User Query: "Should I buy more banking stocks given the recent RBI policy?"

AI Response: "Based on current market conditions and your portfolio 
composition, I recommend cautious exposure to banking stocks. Your current 
banking allocation is 35%, which is already near the optimal range for 
your moderate risk profile. Consider the following factors:

1. Interest Rate Environment: Recent RBI policy suggests...
2. Portfolio Balance: Additional banking exposure would increase concentration risk...
3. Suggested Action: If you proceed, limit to 5% additional exposure..."
```

### 3. Stress Testing Before Major Events
```python
# Run stress test before earnings season
stress_results = await scenario_agent.run_stress_tests(investor_profile)
if stress_results['market_crash']['projected_loss'] > threshold:
    suggest_hedging_strategies()
```

## 🎯 Advanced Features

### Machine Learning Integration
- **Pattern Recognition**: Identify recurring risk patterns
- **Predictive Analytics**: Forecast potential risk events
- **Adaptive Learning**: Agents improve based on outcomes
- **Personalization**: Customized recommendations per investor

### Real-time Features
- **Live Risk Scoring**: Continuous risk assessment
- **Market Event Detection**: Real-time market anomaly detection
- **Instant Alerts**: Immediate notification of high-risk situations
- **Dynamic Rebalancing**: Automated portfolio optimization suggestions

### Integration Capabilities
- **Fyers API**: Live Indian market data
- **Multiple Exchanges**: NSE, BSE, MCX support
- **External Data**: Economic indicators, news sentiment
- **Third-party Tools**: Integration with other financial platforms

## 🚨 Troubleshooting

### Common Issues

#### 1. AWS Bedrock Connection Failed
```
Solution:
1. Check AWS credentials: aws sts get-caller-identity
2. Verify Bedrock permissions in IAM
3. Ensure service is available in your region
4. Check network connectivity
```

#### 2. Market Data Not Loading
```
Solution:
1. Check YFinance availability
2. Verify internet connection
3. Check symbol formats (use .NS for NSE stocks)
4. Review rate limiting settings
```

#### 3. Database Errors
```
Solution:
1. Check database file permissions
2. Verify SQLite installation
3. Check disk space
4. Review database schema
```

### Performance Optimization
- **Caching**: Market data and AI responses cached
- **Async Processing**: Non-blocking AI agent operations
- **Connection Pooling**: Efficient database connections
- **Rate Limiting**: Prevent API abuse

## 📚 Documentation & Support

### Additional Resources
- **API Documentation**: Complete endpoint documentation
- **Agent Behavior Guide**: Detailed agent decision logic
- **Configuration Reference**: All settings explained
- **Best Practices**: Recommended usage patterns

### Getting Help
1. **Check Logs**: Review Flask application logs
2. **Run Tests**: Use `test_risk_management.py` for diagnostics
3. **Review Config**: Verify all configuration settings
4. **AWS Console**: Check Bedrock service status

## 🔮 Future Enhancements

### Planned Features
- **Multi-language Support**: Support for regional languages
- **Mobile App**: Native mobile applications
- **Advanced Visualizations**: 3D risk modeling
- **Social Trading**: Community-based risk insights
- **Options Strategies**: Advanced derivatives analysis

### Scalability Improvements
- **Microservices**: Split agents into separate services
- **Kubernetes**: Container orchestration
- **Event-driven Architecture**: Real-time event processing
- **Multi-region Deployment**: Global availability

## 🏆 Success Metrics

### Key Performance Indicators
- **Risk Prediction Accuracy**: >85% accuracy in risk alerts
- **Response Time**: <2 seconds for API responses
- **System Uptime**: >99.9% availability
- **User Engagement**: Active usage of AI recommendations

### Value Delivered
- **Risk Reduction**: Measurable decrease in portfolio risk
- **Compliance Improvement**: Automated regulatory adherence
- **Decision Quality**: Data-driven investment decisions
- **Time Savings**: Automated risk monitoring and analysis

---

## 💡 Getting Started Checklist

- [ ] Run `python setup_risk_management.py`
- [ ] Configure AWS Bedrock credentials
- [ ] Test system with `python test_risk_management.py`
- [ ] Start Flask app with `python app.py`
- [ ] Visit risk management dashboard
- [ ] Try sample queries with AI advisor
- [ ] Run comprehensive risk analysis
- [ ] Configure risk thresholds
- [ ] Set up production environment (optional)

**🎉 Your AI-powered risk management system is ready to protect and optimize your investments!**

---

*For technical support or feature requests, please check the system logs and run the test suite for diagnostics.*
