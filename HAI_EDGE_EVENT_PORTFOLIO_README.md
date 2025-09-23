# hAi-Edge Event Portfolio Management System

## Overview

The hAi-Edge Event Portfolio Management System is an advanced AI-powered solution that creates dynamic investment portfolios based on real-time market events and news analysis. This system integrates seamlessly with the existing PredictRAM platform to provide intelligent, event-driven portfolio recommendations.

## Key Features

### 🤖 AI-Powered Event Analysis

- **Real-time Event Processing**: Analyzes live market events from multiple sources
- **Sentiment Analysis**: Determines market sentiment (positive, negative, neutral)
- **Impact Assessment**: Calculates event magnitude and market correlation
- **Sector Impact Mapping**: Identifies which sectors will be most affected

### 📊 Dynamic Portfolio Creation

- **Smart Stock Selection**: AI selects relevant stocks based on event analysis
- **Optimal Weighting**: Calculates portfolio weights using advanced algorithms
- **Risk Assessment**: Determines appropriate risk levels for each portfolio
- **Strategy Matching**: Assigns investment strategies based on event characteristics

### 🎯 Performance Tracking

- **Real-time Updates**: Tracks portfolio performance with live market data
- **Risk Metrics**: Calculates Sharpe ratio, volatility, and maximum drawdown
- **Benchmark Comparison**: Compares performance against market benchmarks
- **Historical Analysis**: Maintains performance history for backtesting

### 👥 Admin Management

- **Draft Creation**: Admins can create and review portfolios before publishing
- **Publishing Control**: Secure publishing workflow for investor access
- **Performance Monitoring**: Track all portfolios from a centralized dashboard
- **Event Analytics**: Detailed event impact analysis and recommendations

## System Architecture

### Database Models

#### HAiEdgeEventModel

Main portfolio model containing:

- Event information and metadata
- Portfolio strategy and configuration
- AI analysis and reasoning
- Performance metrics
- Publishing status

#### HAiEdgeEventModelStock

Individual stock holdings:

- Stock symbol and company details
- Portfolio weight and recommendation
- Price targets and stop losses
- Event correlation analysis

#### HAiEdgeEventModelPerformance

Performance tracking:

- Daily returns and cumulative performance
- Risk metrics and benchmark comparison
- Historical performance data

#### HAiEdgeEventModelAnalytics

Detailed event analytics:

- Sentiment and magnitude analysis
- Sector impact predictions
- Key factors and risk assessment

### Service Layer

#### HAiEdgeEventPortfolioService

Core business logic:

- Event analysis algorithms
- Stock selection and weighting
- Performance calculations
- Portfolio optimization

### API Endpoints

| Endpoint                                | Method | Description               |
| --------------------------------------- | ------ | ------------------------- |
| `/hai_edge_event_portfolios`            | GET    | Main dashboard            |
| `/api/analyze_event_for_portfolio`      | POST   | Analyze event suitability |
| `/api/create_event_portfolio`           | POST   | Create new portfolio      |
| `/api/publish_event_portfolio`          | POST   | Publish portfolio         |
| `/api/get_event_portfolio_details/{id}` | GET    | Get portfolio details     |
| `/api/portfolio_performance/{id}`       | GET    | Get performance metrics   |
| `/api/delete_event_portfolio`           | POST   | Delete draft portfolio    |

## Usage Guide

### For Administrators

#### 1. Access the Dashboard

Navigate to `http://localhost:80/hai_edge_event_portfolios`

#### 2. Review Live Events

- View real-time market events from the Enhanced Events Analytics
- Check suitability scores for portfolio creation
- Events with scores >60% are recommended for portfolio creation

#### 3. Create Portfolios

1. Click "Create Portfolio" on suitable events
2. Review AI analysis and stock recommendations
3. Confirm portfolio creation
4. Portfolio is created in "Draft" status

#### 4. Manage Portfolios

- Review draft portfolios before publishing
- Check performance metrics and analytics
- Publish portfolios to make them available to investors
- Delete unsuitable draft portfolios

#### 5. Monitor Performance

- Track real-time portfolio performance
- Review risk metrics and returns
- Compare against benchmarks
- Analyze historical performance

### For Investors

#### Access Published Portfolios

- Published portfolios appear in the main portfolio list
- View detailed analytics and stock holdings
- Track performance and returns
- Access AI reasoning behind portfolio creation

## AI Analysis Components

### Event Suitability Scoring

The system evaluates events based on:

- **Magnitude (40%)**: How significant the event is (0-10 scale)
- **Confidence (30%)**: AI confidence in the analysis (0-1)
- **Probability (20%)**: Likelihood of predicted outcome (0-1)
- **Sector Impact (10%)**: Breadth of market impact

### Stock Selection Algorithm

1. **Sector Mapping**: Identify affected market sectors
2. **Stock Pool Analysis**: Select from curated stock pools by sector
3. **Impact Scoring**: Calculate individual stock correlation to event
4. **Weight Distribution**: Optimize portfolio weights based on impact scores
5. **Risk Balancing**: Ensure appropriate diversification and risk levels

### Performance Metrics

- **Total Return**: Portfolio return vs initial value
- **Sharpe Ratio**: Risk-adjusted return metric
- **Maximum Drawdown**: Largest peak-to-trough decline
- **Volatility**: Standard deviation of returns
- **Alpha**: Excess return vs benchmark

## Configuration and Customization

### Stock Pools

Customize stock pools by sector in `hai_edge_event_portfolio_service.py`:

```python
self.stock_pools = {
    'technology': ['AAPL', 'MSFT', 'GOOGL', ...],
    'healthcare': ['JNJ', 'PFE', 'UNH', ...],
    # Add more sectors and stocks
}
```

### Risk Thresholds

Adjust suitability thresholds:

```python
if suitability_score >= 0.6:  # Adjust threshold
    # Create portfolio
```

### Performance Updates

Set up automated performance updates using the background API:

```python
# Call periodically
/api/update_portfolio_performance
```

## Integration Points

### Enhanced Events Analytics

- Seamless integration with existing event analysis system
- Real-time event data feeds
- Event pattern recognition and prediction

### Existing Portfolio Systems

- Compatible with current PredictRAM models
- Shared database infrastructure
- Unified admin interface

### Market Data Sources

- Yahoo Finance integration for real-time prices
- Support for additional data providers
- Caching layer for performance optimization

## Security and Access Control

### Admin Features

- Secure portfolio creation and publishing
- Access control for management functions
- Audit trail for all portfolio operations

### Investor Access

- Read-only access to published portfolios
- Performance tracking and analytics
- Secure data transmission

## Monitoring and Maintenance

### Health Checks

- Database connectivity monitoring
- API endpoint availability
- Performance metric updates

### Logging

- Comprehensive error logging
- Performance tracking
- User activity monitoring

### Backup and Recovery

- Regular database backups
- Portfolio data preservation
- Disaster recovery procedures

## Future Enhancements

### Planned Features

- **Advanced ML Models**: Deep learning for event analysis
- **Real-time Rebalancing**: Dynamic portfolio adjustments
- **Social Sentiment**: Social media sentiment integration
- **Options Strategies**: Complex derivatives portfolios
- **Multi-asset Classes**: Bonds, commodities, currencies

### API Expansions

- RESTful API for third-party integrations
- Webhook notifications for portfolio updates
- Bulk portfolio operations
- Advanced filtering and search

## Support and Troubleshooting

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running
2. **Missing Dependencies**: Install required Python packages
3. **API Errors**: Check error logs in console output
4. **Performance Issues**: Monitor database query performance

### Error Codes

- `400`: Bad Request - Invalid input data
- `403`: Forbidden - Admin access required
- `404`: Not Found - Portfolio not found
- `500`: Internal Server Error - System error

### Debug Mode

Enable debug logging in `app.py`:

```python
app.debug = True
```

## Contact and Support

For technical support and feature requests, please refer to the main PredictRAM documentation or contact the development team.

---

_hAi-Edge Event Portfolio Management System - Powered by Advanced AI and Machine Learning_
