# ML Model Performance Tracking System

## Overview

This system provides comprehensive performance tracking for published ML models that make stock recommendations. It automatically extracts stock recommendations from model outputs, tracks their performance over time, and provides detailed analytics.

## Features

### 🤖 Automatic Recommendation Extraction

- Parses ML model outputs to identify stock recommendations (BUY/SELL/HOLD)
- Extracts confidence scores, target prices, and stop-loss levels
- Supports multiple output formats and patterns

### 📈 Real-time Performance Tracking

- Daily stock price updates (fetched once per day to respect API limits)
- Calculates returns for different time periods (1D, 1W, 1M, 3M, 6M, 1Y)
- Tracks win rates, average returns, and risk metrics

### 📊 Comprehensive Analytics

- **Return Metrics**: Total return, average return, best/worst trades
- **Risk Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown, volatility
- **Portfolio Simulation**: Simulated $10,000 portfolio value tracking
- **Benchmark Comparison**: Alpha and beta vs S&P 500
- **Sector Analysis**: Performance breakdown by industry sector

### 🎯 Performance Periods

- **1 Week**: Short-term performance tracking
- **1 Month**: Monthly performance analysis
- **3 Months**: Quarterly performance review
- **6 Months**: Semi-annual tracking
- **1 Year**: Annual performance metrics
- **All Time**: Complete historical performance

## Setup Instructions

### 1. Install Dependencies

```bash
python setup_performance_tracking.py
```

This will install required packages:

- `schedule` - for daily price updates
- `pandas` - for data manipulation
- `yfinance` - for stock price data

### 2. Database Setup

The setup script automatically creates the required database tables:

- `model_recommendations` - Stock recommendations from ML models
- `stock_price_history` - Daily OHLCV price data
- `model_performance_metrics` - Aggregated performance metrics

### 3. Start the Application

```bash
python app.py
```

### 4. Test the System

```bash
python manual_performance_update.py
```

## How It Works

### 1. Recommendation Extraction

When a published ML model is run, the system automatically:

- Analyzes the output text for stock recommendations
- Uses pattern matching to identify BUY/SELL/HOLD signals
- Extracts additional data like confidence scores and target prices
- Saves recommendations to the database with current stock prices

### 2. Daily Price Updates

Once per day (configurable), the system:

- Fetches current prices for all tracked stocks using Yahoo Finance
- Updates the `stock_price_history` table
- Calculates current returns for all active recommendations
- Runs automatically in the background

### 3. Performance Calculation

The system calculates comprehensive metrics:

- **Individual Trade Performance**: Return per recommendation
- **Aggregate Metrics**: Win rate, average return, total return
- **Risk Adjusted Returns**: Sharpe ratio, Sortino ratio
- **Portfolio Simulation**: Tracks hypothetical $10,000 investment
- **Benchmark Comparison**: Performance vs S&P 500

## Supported Recommendation Patterns

The system recognizes various output formats:

### Pattern 1: Simple Format

```
BUY AAPL @ $150
SELL TSLA @ $800
HOLD MSFT
```

### Pattern 2: Structured Format

```
Stock: AAPL, Action: BUY, Price: 150, Target: 170, Stop: 140
Stock: TSLA, Action: SELL, Price: 800, Confidence: 85%
```

### Pattern 3: Detailed Format

```
Symbol: AAPL | Recommendation: BUY | Target: $170 | Confidence: 90%
Symbol: TSLA | Recommendation: SELL | Stop Loss: $750
```

## API Endpoints

### Performance Data

- `GET /api/published_models/{id}/performance?period={period}` - Get performance metrics
- `GET /api/published_models/{id}/recommendations` - Get all recommendations
- `GET /api/published_models/{id}/performance/charts` - Get chart data

### Admin Operations

- `POST /api/admin/performance/update_prices` - Manual price update
- `POST /api/admin/performance/calculate_metrics` - Manual metrics calculation

## Web Interface

### Published Models Catalog

Access the performance tracking interface at: `http://127.0.0.1:80/published`

Each model card now includes:

- **Performance Button**: View detailed performance analytics
- **Real-time Metrics**: Current win rate and return information
- **Visual Indicators**: Performance status and risk levels

### Performance Dialog

Click the "Performance" button on any model to view:

- **Key Metrics Grid**: Total return, win rate, Sharpe ratio, portfolio value
- **Recent Recommendations Table**: Latest stock picks with current returns
- **Performance Charts**: Portfolio value over time, sector breakdown
- **Period Selector**: View performance for different time windows

## Daily Updates

### Automatic Scheduling

For production deployments, set up the daily update script to run automatically:

#### Linux/Mac (Cron)

```bash
# Add to crontab (crontab -e)
0 18 * * * /path/to/python /path/to/daily_performance_update.py
```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set to run daily at 6:00 PM
4. Action: Start a program
5. Program: python.exe
6. Arguments: daily_performance_update.py
7. Start in: [app directory]

### Manual Updates

For testing or immediate updates:

```bash
python manual_performance_update.py
```

## Configuration

### Stock Data Source

The system uses Yahoo Finance via the `yfinance` library:

- Free and reliable
- No API key required
- Comprehensive market data
- Handles stock splits and dividends

### Price Update Frequency

- **Default**: Once per day at 6 PM EST (after market close)
- **Rationale**: Respects API rate limits and provides sufficient data
- **Customizable**: Modify the schedule in the daily update script

### Performance Periods

All periods are calculated relative to the current date:

- **1W**: Last 7 days
- **1M**: Last 30 days
- **3M**: Last 90 days
- **6M**: Last 180 days
- **1Y**: Last 365 days
- **ALL**: All available data

## Performance Metrics Explained

### Return Metrics

- **Total Return**: Sum of all recommendation returns
- **Average Return**: Mean return per recommendation
- **Win Rate**: Percentage of profitable recommendations
- **Best/Worst**: Highest and lowest individual returns

### Risk Metrics

- **Sharpe Ratio**: Risk-adjusted return (return per unit of volatility)
- **Sortino Ratio**: Downside risk-adjusted return
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Volatility**: Standard deviation of returns

### Portfolio Simulation

- **Starting Value**: $10,000 hypothetical investment
- **Current Value**: Value after applying all recommendation returns
- **Benchmark**: Comparison to S&P 500 performance
- **Alpha**: Excess return vs benchmark
- **Beta**: Correlation with market movements

## Troubleshooting

### Common Issues

#### No Performance Data

- **Cause**: Model hasn't generated extractable recommendations
- **Solution**: Ensure model outputs follow supported patterns

#### Price Update Failures

- **Cause**: Network issues or Yahoo Finance rate limits
- **Solution**: Run manual update, check internet connection

#### Missing Metrics

- **Cause**: Insufficient recommendation history
- **Solution**: Generate more recommendations, wait for data accumulation

### Debug Commands

```bash
# Check database tables
python -c "from app import app, db; app.app_context().push(); print(db.engine.table_names())"

# Test price fetching
python -c "import yfinance as yf; print(yf.Ticker('AAPL').history(period='1d'))"

# Check performance tracker
python -c "from app import app, performance_tracker; print(performance_tracker)"
```

### Logs

Monitor the application logs for:

- Recommendation extraction results
- Price update status
- Performance calculation progress
- Error messages and warnings

## Future Enhancements

### Planned Features

- **Options Trading**: Support for options recommendations
- **Crypto Tracking**: Cryptocurrency recommendation performance
- **Social Sentiment**: Integration with social media sentiment
- **Advanced Charts**: Interactive charts with Chart.js/D3.js
- **Email Alerts**: Automated performance reports
- **Mobile Interface**: Responsive design optimization

### Integration Opportunities

- **Portfolio Management**: Link with brokerage APIs
- **Risk Management**: Real-time position sizing
- **Backtesting**: Historical strategy validation
- **Machine Learning**: Performance prediction models

## Support

### Getting Help

1. Check the application logs for error messages
2. Run the manual update script to test functionality
3. Verify database connectivity and table creation
4. Ensure Yahoo Finance is accessible from your network

### Contributing

The performance tracking system is modular and extensible. Key areas for contribution:

- Additional recommendation pattern recognition
- Enhanced chart visualizations
- Alternative data sources
- Performance metric calculations
- Risk management features

---

_Last updated: August 2025_
