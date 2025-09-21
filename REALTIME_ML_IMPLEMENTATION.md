# Real-time ML Models with Fyers API Integration

## Overview

This implementation adds real-time ML model capabilities to the PredictRAM platform, featuring:

- **Real-time data fetching** using Fyers API with YFinance fallback
- **Enhanced ML models** with live market data integration
- **Symbol mapping system** for Fyers ↔ YFinance symbol conversion
- **Admin dashboard** for API management and model execution
- **Investor dashboard integration** for real-time recommendations

## Features

### 🚀 Real-time Data Sources

1. **Fyers API Integration**
   - Live market data from Fyers
   - Real-time price quotes
   - Professional data quality
   - Admin-configurable API keys

2. **YFinance Fallback**
   - Automatic fallback when Fyers unavailable
   - Free data source
   - Reliable for development/testing

### 🧠 Enhanced ML Models

1. **Real-time Stock Recommender**
   - Live technical analysis
   - ML-based recommendations (BUY/SELL/HOLD)
   - Confidence scoring
   - Real-time price targets and stop losses

2. **Real-time BTST Analyzer**
   - Buy Today Sell Tomorrow opportunities
   - Momentum and volume analysis
   - Risk-adjusted scoring
   - Overnight gap predictions

3. **Real-time Options Analyzer**
   - Options strategy recommendations
   - Volatility analysis
   - Strike price suggestions
   - Risk assessment

4. **Real-time Sector Analyzer**
   - Sector performance analysis
   - Relative strength comparison
   - Market breadth indicators
   - Sector rotation signals

## File Structure

```
├── realtime_data_fetcher.py      # Core data fetching and symbol mapping
├── realtime_ml_models.py         # Enhanced ML models with real-time capabilities
├── fyers_yfinance_mapping.csv    # Symbol mapping file
├── templates/
│   └── admin_realtime_ml.html    # Admin dashboard for ML models
└── app.py                        # Updated with new API endpoints
```

## Setup Instructions

### 1. Install Required Packages

```bash
pip install yfinance scikit-learn TA-Lib pandas numpy
```

### 2. Configure Fyers API (Optional)

1. Access admin dashboard: `/admin/realtime_ml`
2. Enter Fyers API credentials:
   - **API Key**: Your Fyers API key
   - **Access Token**: Your Fyers access token
   - **Client ID**: Your Fyers client ID (optional)
3. Test connection to verify setup

### 3. Symbol Mapping

The system uses `fyers_yfinance_mapping.csv` to map between Fyers and YFinance symbols:

```csv
fyers_symbol,yfinance_symbol,name
NSE:RELIANCE-EQ,RELIANCE.NS,Reliance Industries Ltd
NSE:TCS-EQ,TCS.NS,Tata Consultancy Services Ltd
...
```

## API Endpoints

### Fyers API Management

- `POST /api/admin/api_keys/save` - Save Fyers API credentials
- `POST /api/admin/fyers/test_connection` - Test Fyers connection
- `GET /api/admin/fyers/get_symbols` - Get symbol mappings
- `GET /api/admin/fyers/real_time_price/<symbol>` - Get real-time price

### Real-time ML Models

- `POST /api/admin/ml_models/run_stock_recommender` - Run stock recommender
- `POST /api/admin/ml_models/run_btst_analyzer` - Run BTST analyzer
- `POST /api/admin/ml_models/run_options_analyzer` - Run options analyzer
- `POST /api/admin/ml_models/run_sector_analyzer` - Run sector analyzer

### Investor Dashboard

- `POST /api/admin/ml_models/run_realtime_investor_recommendations` - Generate comprehensive recommendations

## Usage Examples

### 1. Admin Dashboard

Access the admin dashboard at `/admin/realtime_ml` to:

- Configure Fyers API credentials
- Test real-time data connectivity
- Run individual ML models
- View analysis results

### 2. API Usage

```python
# Example: Run real-time stock recommender
data = {
    'stock_category': 'NIFTY50',
    'min_confidence': 70,
    'use_fyers': True
}

response = requests.post('/api/admin/ml_models/run_stock_recommender', data=data)
```

### 3. Programmatic Integration

```python
from realtime_ml_models import real_time_stock_recommender
from realtime_data_fetcher import RealTimeDataFetcher

# Initialize with Fyers API
fetcher = RealTimeDataFetcher(fyers_api_key="your_key", fyers_access_token="your_token")
real_time_stock_recommender.data_fetcher = fetcher

# Get recommendation
recommendation = real_time_stock_recommender.predict_stock("RELIANCE.NS")
print(recommendation)
```

## Technical Features

### Real-time Data Processing

- **Live Price Feeds**: Get current market prices
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Volume Analysis**: Real-time volume compared to historical averages
- **Market Breadth**: Sector-wise performance tracking

### ML Model Enhancements

- **Feature Engineering**: Real-time technical indicators
- **Confidence Scoring**: Dynamic confidence based on market conditions
- **Risk Management**: Automatic stop-loss and target price calculation
- **Market Regime Detection**: Adapt strategies to current market conditions

### Data Source Management

- **Intelligent Fallback**: Automatic switch to YFinance if Fyers fails
- **Symbol Mapping**: Seamless conversion between different data providers
- **Error Handling**: Robust error handling and logging
- **Performance Optimization**: Efficient data caching and processing

## Configuration

### Database Schema Updates

The implementation extends the existing `AdminAPIKey` model:

```python
class AdminAPIKey(db.Model):
    # Existing fields...
    access_token = db.Column(db.Text)      # For Fyers access token
    client_id = db.Column(db.String(100))  # For Fyers client ID
```

### Environment Variables (Optional)

```bash
FYERS_API_KEY=your_fyers_api_key
FYERS_ACCESS_TOKEN=your_fyers_access_token
FYERS_CLIENT_ID=your_fyers_client_id
```

## Performance Considerations

- **Lazy Loading**: ML models loaded only when needed
- **Connection Pooling**: Efficient API connection management
- **Caching**: Smart caching of frequently accessed data
- **Rate Limiting**: Respect API rate limits
- **Error Recovery**: Graceful degradation on API failures

## Security

- **API Key Encryption**: Secure storage of API credentials in database
- **Admin Access Control**: Restricted access to configuration
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: No sensitive information in error messages

## Monitoring and Logging

- **Connection Status**: Real-time API connection monitoring
- **Performance Metrics**: Track model execution times
- **Error Logging**: Comprehensive error tracking
- **Data Source Tracking**: Monitor which data source is being used

## Troubleshooting

### Common Issues

1. **Fyers API Connection Failed**
   - Verify API credentials
   - Check access token validity
   - Ensure proper network connectivity

2. **Symbol Not Found**
   - Check symbol mapping in CSV file
   - Verify symbol format (NSE:SYMBOL-EQ vs SYMBOL.NS)
   - Try with YFinance fallback

3. **ML Model Errors**
   - Check data availability
   - Verify technical indicator calculations
   - Review confidence thresholds

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **WebSocket Integration**: Real-time streaming data
- **Advanced ML Models**: Deep learning models for predictions
- **Portfolio Integration**: Real-time portfolio tracking
- **Alert System**: Real-time alerts based on ML signals
- **Mobile API**: REST API for mobile applications

## Support

For technical support and questions:

1. Check the troubleshooting section
2. Review API documentation
3. Contact development team
4. Submit bug reports with detailed logs

---

**Note**: This implementation provides a robust foundation for real-time ML trading analysis. The system is designed to be scalable, maintainable, and production-ready.
