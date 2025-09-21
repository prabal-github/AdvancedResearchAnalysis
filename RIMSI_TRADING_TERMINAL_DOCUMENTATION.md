# RIMSI Trading Terminal - Complete Documentation

## Overview

The RIMSI Trading Terminal is a professional AI-powered trading platform that combines real-time market data, agentic AI agents, portfolio management, and advanced analytics into a comprehensive trading solution. The system operates on Flask with PostgreSQL backend and provides both REST APIs and interactive web interfaces.

## Architecture

### Core Components

1. **Flask Application**: Main application server with multiple trading endpoints
2. **Agentic AI System**: Multiple specialized AI agents for trading insights
3. **Real-time Data Service**: Integration with Fyers API and Yahoo Finance
4. **PostgreSQL Database**: Persistent storage for users, portfolios, and analytics
5. **Frontend Templates**: Professional trading interfaces with real-time updates

### System Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask App      │    │   Database      │
│   Templates     │◄──►│   Trading APIs   │◄──►│   PostgreSQL    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Real-time UI   │    │  Agentic AI      │    │  Data Models    │
│  Updates        │    │  Meta-Agents     │    │  & Analytics    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Main Endpoints

### 1. Trading Terminal Home
**URL**: `http://127.0.0.1:5008/rimsi_trading_terminal`
**Method**: GET
**Description**: Main trading terminal interface with AI agents

**Function**: `rimsi_trading_terminal_page()`
**Location**: Lines 17095-17140 in app.py

**Features**:
- Creates demo investor session automatically
- Initializes AI trading environment
- Renders professional trading interface
- Session management and authentication

**Template**: `trading_terminal.html`
- Grid-based layout with sidebar, main content, and right panel
- Real-time status indicators
- AI agent control panel
- Command interface for natural language queries

### 2. Portfolio Management
**URL**: `http://127.0.0.1:5008/rimsi_trading_terminal_portfolio`
**Method**: GET
**Description**: Portfolio analysis and management interface

**Function**: `rimsi_trading_terminal_portfolio()`
**Location**: Lines 61750-61770 in app.py

**Features**:
- Portfolio creation and management
- Real-time performance tracking
- Risk analytics and recommendations
- Asset allocation visualization

**Template**: `rimsi_trading_terminal_portfolio.html`
- Professional portfolio dashboard
- Interactive charts and metrics
- Portfolio creation forms
- Performance analytics

## API Endpoints

### 1. Agent Status API
**URL**: `/api/trading_terminal/agent_status`
**Method**: GET
**Description**: Get status of all active trading agents

**Response Format**:
```json
{
  "success": true,
  "agents": [
    {
      "name": "Alpha Trader",
      "status": "active",
      "performance": "85.2%",
      "last_signal": "2024-01-15T10:30:00Z"
    }
  ],
  "system_status": "active",
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### 2. AI Insights API
**URL**: `/api/trading_terminal/insights`
**Method**: GET
**Parameters**: `limit` (optional, default: 10)
**Description**: Get recent insights from trading agents

**Response Format**:
```json
{
  "success": true,
  "insights": [
    {
      "agent": "Alpha Trader",
      "insight": "Strong bullish momentum in RELIANCE",
      "confidence": 0.85,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "count": 5,
  "timestamp": "2024-01-15T10:35:00Z"
}
```

### 3. AI Query Processing API
**URL**: `/api/trading_terminal/query`
**Method**: POST
**Description**: Process natural language queries from users

**Request Format**:
```json
{
  "query": "What are the best stocks to buy today?"
}
```

**Response Format**:
```json
{
  "success": true,
  "response": "Based on current market analysis...",
  "recommendations": [...],
  "confidence": 0.82,
  "sources": ["Alpha Trader", "Market Scanner"]
}
```

### 4. Portfolio Analysis API
**URL**: `/api/trading_terminal/portfolio_analysis`
**Method**: POST
**Description**: Get comprehensive portfolio analysis with real-time data

**Features**:
- Real-time portfolio valuation
- P&L calculations with live prices
- Risk metrics and analytics
- Sector allocation analysis
- AI-powered recommendations

**Response Format**:
```json
{
  "success": true,
  "portfolio_summary": {
    "total_invested": 1000000.00,
    "current_value": 1050000.00,
    "total_pnl": 50000.00,
    "total_pnl_percent": 5.0,
    "day_pnl": 2500.00,
    "day_pnl_percent": 0.24
  },
  "holdings": [
    {
      "symbol": "RELIANCE",
      "quantity": 100,
      "avg_price": 2500.00,
      "current_price": 2525.00,
      "invested_value": 250000.00,
      "current_value": 252500.00,
      "pnl": 2500.00,
      "pnl_percent": 1.0,
      "day_change": 0.5,
      "day_pnl": 1250.00
    }
  ],
  "sector_allocation": {
    "Banking": 35.0,
    "IT": 30.0,
    "Energy": 25.0,
    "Others": 10.0
  },
  "analysis": {
    "overall_score": 7.5,
    "risk_score": 6.2,
    "diversification_score": 8.5,
    "performance_score": 7.0,
    "recommendations": [...],
    "metrics": {
      "sharpe_ratio": 1.85,
      "max_drawdown": 12.3,
      "var_95": 50000,
      "correlation_avg": 0.28
    }
  }
}
```

### 5. Market Scan API
**URL**: `/api/trading_terminal/market_scan`
**Method**: GET
**Parameters**: `type` (momentum, value, breakout)
**Description**: AI-powered market scanning for trading opportunities

**Scan Types**:
- **Momentum**: High-moving stocks with volume surge
- **Value**: Undervalued stocks with good fundamentals
- **Breakout**: Stocks breaking technical resistance levels

**Response Format**:
```json
{
  "success": true,
  "scan_type": "momentum",
  "results": [
    {
      "symbol": "TATAMOTORS",
      "price": 965.50,
      "change": 5.8,
      "volume_ratio": 3.2,
      "rsi": 78,
      "score": 9.0
    }
  ],
  "count": 10,
  "timestamp": "2024-01-15T10:35:00Z",
  "data_source": "Fyers API"
}
```

### 6. Real-time Data API
**URL**: `/api/trading_terminal/real_time_data`
**Method**: GET
**Description**: Get real-time market data for terminal display

**Features**:
- Market indices (NIFTY, BANK NIFTY, VIX)
- FII/DII flows
- Watchlist stocks with live prices
- Market status and timing

**Response Format**:
```json
{
  "success": true,
  "market_data": {
    "nifty": {
      "value": 20085.50,
      "change": 1.2,
      "change_percent": 0.06
    },
    "bank_nifty": {
      "value": 45280.25,
      "change": 2.5,
      "change_percent": 0.06
    },
    "vix": {
      "value": 15.25,
      "change": -0.3
    },
    "fii_dii": {
      "fii_flow": 2500,
      "dii_flow": 1200
    }
  },
  "watchlist": [...],
  "timestamp": "2024-01-15T10:35:00Z",
  "market_status": "open",
  "data_source": "Fyers API"
}
```

### 7. Stock Recommendations API
**URL**: `/api/trading_terminal/stock_recommendations`
**Method**: GET
**Description**: Get AI-powered stock recommendations from multiple agents

**AI Agents**:
- **Alpha Trader**: Focus on momentum and fundamentals
- **Beta Optimizer**: Focus on risk-adjusted returns
- **Gamma Scanner**: Focus on technical patterns and breakouts

**Response Format**:
```json
{
  "success": true,
  "recommendations": [
    {
      "symbol": "RELIANCE",
      "currentPrice": 2645.50,
      "recommendedPrice": 2620.00,
      "targetPrice": 2850.00,
      "stopLoss": 2480.00,
      "recommendation": "BUY",
      "agent": "Alpha Trader",
      "confidence": 0.85,
      "reasoning": "Strong fundamentals, expanding digital presence...",
      "timestamp": "2024-01-15T10:35:00Z"
    }
  ],
  "agents_active": ["Alpha Trader", "Beta Optimizer", "Gamma Scanner"],
  "market_conditions": {
    "trend": "bullish",
    "volatility": "moderate",
    "sentiment": "positive"
  }
}
```

## AI Agent System

### Agentic AI Architecture

The system implements multiple specialized AI agents:

1. **Alpha Trader Agent**
   - Focus: Momentum and fundamental analysis
   - Specialties: Growth stocks, sector rotation
   - Risk Profile: Moderate to aggressive

2. **Beta Optimizer Agent**
   - Focus: Risk-adjusted returns
   - Specialties: Portfolio optimization, risk management
   - Risk Profile: Conservative to moderate

3. **Gamma Scanner Agent**
   - Focus: Technical analysis and breakouts
   - Specialties: Pattern recognition, entry/exit timing
   - Risk Profile: Tactical trading

### Meta-Agent Controller

**Function**: `AgenticAIMasterController`
**Features**:
- Orchestrates multiple AI agents
- Consensus-based decision making
- Real-time performance monitoring
- Dynamic agent allocation

## Data Integration

### Real-time Data Sources

1. **Fyers API** (Production)
   - Live market data
   - Historical charts
   - Order management
   - Portfolio tracking

2. **Yahoo Finance** (Development/Fallback)
   - Market quotes
   - Historical data
   - Basic analytics

### Data Service Architecture

**Module**: `real_time_data_service.py`
**Functions**:
- `get_real_time_service()`: Initialize data service
- `get_stock_quote()`: Get live stock prices
- `get_multiple_quotes()`: Bulk quote retrieval
- `get_market_indices()`: Index data
- `calculate_technical_indicators()`: Technical analysis

## Security & Authentication

### Session Management
- Demo investor sessions for testing
- Automatic session creation
- Session-based portfolio tracking

### API Security
- Error handling and fallback systems
- Rate limiting considerations
- Data validation and sanitization

## Frontend Features

### Trading Terminal Interface

**File**: `trading_terminal.html`
**Features**:
- Professional dark theme
- Real-time status indicators
- AI agent control panel
- Command-line interface for queries
- Multi-panel layout (sidebar, main, right panel)

**CSS Framework**: Custom CSS with professional styling
**JavaScript**: Real-time updates and API integration

### Portfolio Interface

**File**: `rimsi_trading_terminal_portfolio.html`
**Features**:
- Portfolio creation and management
- Real-time performance metrics
- Interactive charts and graphs
- Risk analytics dashboard

## Installation & Setup

### Prerequisites
```bash
# Python packages
pip install flask sqlalchemy psycopg2-binary requests yfinance

# Database
PostgreSQL with connection: postgresql://admin:admin%402001@3.85.19.80:5432/research
```

### Environment Setup
```python
# Environment variables
FLASK_ENV=development
DATABASE_URL=postgresql://admin:admin%402001@3.85.19.80:5432/research
FYERS_API_KEY=your_fyers_key  # For production
```

### Running the Application
```bash
# Start Flask application
python app.py

# Access trading terminal
http://127.0.0.1:5008/rimsi_trading_terminal

# Access portfolio manager
http://127.0.0.1:5008/rimsi_trading_terminal_portfolio
```

## API Usage Examples

### Get Agent Status
```bash
curl -X GET http://127.0.0.1:5008/api/trading_terminal/agent_status
```

### Process AI Query
```bash
curl -X POST http://127.0.0.1:5008/api/trading_terminal/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me top momentum stocks"}'
```

### Get Portfolio Analysis
```bash
curl -X POST http://127.0.0.1:5008/api/trading_terminal/portfolio_analysis \
  -H "Content-Type: application/json"
```

### Market Scan
```bash
curl -X GET "http://127.0.0.1:5008/api/trading_terminal/market_scan?type=momentum"
```

## Performance Features

### Real-time Updates
- Live price feeds
- Real-time P&L calculations
- Dynamic portfolio valuation
- Market status monitoring

### Fallback Systems
- Graceful degradation when APIs fail
- Simulated data for development
- Error handling and recovery

### Optimization
- Async data processing
- Efficient database queries
- Caching for improved performance

## Development Guidelines

### Adding New Features
1. Define API endpoints in `app.py`
2. Create corresponding templates in `templates/`
3. Implement data services in respective modules
4. Add error handling and fallback systems

### Testing
- Use localhost environment for development
- Demo investor sessions for testing
- Fallback data for offline development

### Deployment
- Configure Fyers API for production
- Set up proper database connections
- Enable production optimizations

## Troubleshooting

### Common Issues
1. **Database Connection**: Check PostgreSQL connection string
2. **API Failures**: Ensure Fyers API credentials are correct
3. **Session Issues**: Clear browser cookies for fresh sessions
4. **Real-time Data**: Check network connectivity and API limits

### Debug Mode
- Enable Flask debug mode for development
- Check browser console for JavaScript errors
- Monitor Flask logs for backend issues

### Support
- Check application logs for error details
- Verify database connectivity
- Test API endpoints individually

---

This documentation provides a comprehensive overview of the RIMSI Trading Terminal system, including all endpoints, features, and implementation details.