# ML Models Dashboard - Admin Feature

This feature adds a comprehensive ML Models dashboard for administrators to run advanced stock analysis using two powerful Python models.

## 🚀 Features

### 1. Advanced Stock Recommender Model
- **Multi-model technical analysis** with risk assessment
- **Technical Indicators**: RSI, MACD, Bollinger Bands, ATR, TSI, Support/Resistance, Candlestick Patterns
- **Accuracy**: 87% | **Problem Solving**: 90%
- **Outputs**: Buy/Sell/Neutral recommendations with confidence scores, stop-loss, and target prices

### 2. Overnight Edge BTST Analyzer
- **Buy Today Sell Tomorrow** analysis for short-term trading opportunities
- **BTST Score Calculation** (0-100 scale)
- **Advanced Features**:
  - Overnight Gap Analysis
  - Volume Spike Detection
  - Close Near High Analysis
  - Advanced Risk-Reward Calculation

## 📊 Key Components

### Database Models
- `MLModelResult`: Store ML model execution results
- `StockRecommenderResult`: Individual stock recommendations
- `BTSTAnalysisResult`: BTST analysis results
- `StockCategory`: Stock categories from stocklist.xlsx

### API Endpoints
- `GET /admin/ml_models` - ML Models dashboard
- `POST /api/admin/ml_models/run_stock_recommender` - Run stock recommender
- `POST /api/admin/ml_models/run_btst_analyzer` - Run BTST analyzer
- `GET /api/admin/stock_categories` - Get stock categories
- `GET /api/admin/ml_results/recent` - Get recent results
- `GET /api/admin/ml_results/<id>` - Get specific result
- `GET /api/admin/ml_results/<id>/download` - Download result as JSON
- `GET /api/ml_results/<id>` - Public API for results

## 🛠️ Setup Instructions

### 1. Database Setup
```bash
python setup_ml_models.py
```
This will:
- Create necessary database tables
- Load default stock categories
- Test the setup

### 2. Test Models
```bash
python test_ml_models.py
```
This will verify:
- Model imports work correctly
- Database integration is functional
- Sample analysis runs successfully

### 3. Stock Categories Configuration
The system supports multiple ways to load stock categories:

#### Option A: Excel File (Recommended)
Place `stocklist.xlsx` in the `stockdata/` directory with columns:
- `Category`: Category name (e.g., "NSE_LARGE_CAP")
- `Symbol`: Stock symbol (e.g., "RELIANCE")

#### Option B: Default Categories
If no Excel file is found, the system uses these default categories:
- NSE_LARGE_CAP (10 stocks)
- NSE_MID_CAP (8 stocks)
- NSE_SMALL_CAP (5 stocks)
- BANKING (8 stocks)
- IT_SECTOR (5 stocks)
- AUTO_SECTOR (4 stocks)
- PHARMA_SECTOR (5 stocks)
- FMCG_SECTOR (5 stocks)

## 📈 Usage Guide

### Access the Dashboard
1. Login as admin
2. Navigate to Admin Dashboard
3. Click "ML Models" button
4. You'll see the ML Models Dashboard

### Running Advanced Stock Recommender
1. Click "Run Analysis" on the Advanced Stock Recommender card
2. Select a stock category from the dropdown
3. Adjust the minimum confidence percentage (50-90%)
4. Click "Run Analysis"
5. View results in the modal with detailed table

### Running BTST Analyzer
1. Click "Run Analysis" on the Overnight Edge BTST card
2. Select a stock category
3. Set minimum confidence percentage
4. Set BTST minimum score (50-100)
5. Click "Run Analysis"
6. View BTST-specific results including scores and risk metrics

### Result Features
- **Real-time Analysis**: Fresh market data analysis
- **Detailed Results**: Comprehensive technical indicators
- **API Access**: Each result gets a unique API endpoint
- **Download**: JSON format for external use
- **History**: View recent analysis runs

## 📋 Result Columns

### Advanced Stock Recommender Results
| Column | Description |
|--------|-------------|
| Symbol | Stock symbol |
| Current Price | Latest stock price |
| Change (%) | Daily price change |
| Open/High/Low | OHLC data |
| Volume | Trading volume |
| RSI (14) | Relative Strength Index |
| SMA (20/50) | Simple Moving Averages |
| MACD | Moving Average Convergence Divergence |
| Bollinger Band | Support and resistance levels |
| Recommendation | Buy/Sell/Neutral |
| Confidence (%) | Model confidence score |
| Stop Loss | Recommended stop loss price |
| Target | Target price |
| Condition | Primary analysis condition |
| Trend (S/M) | Short/Medium term trend |
| Data Freshness | Real-time indicator |
| Last Updated | Analysis timestamp |

### BTST Analyzer Results
| Column | Description |
|--------|-------------|
| Symbol | Stock symbol |
| Current Price | Latest stock price |
| Change (%) | Daily price change |
| BTST Score | BTST opportunity score (0-100) |
| RSI (14) | Relative Strength Index |
| Volume Spike | Volume increase factor |
| Recommendation | BUY/SELL/HOLD/BTST_BUY |
| Confidence (%) | Model confidence score |
| Risk-Reward Ratio | Risk to reward ratio |
| Stop Loss | Recommended stop loss |
| Target | Target price |

## 🔧 Technical Implementation

### Model Architecture
- **Advanced Stock Recommender**: Multi-model ensemble using Open-High/Low conditions, technical indicators, and risk assessment
- **BTST Analyzer**: Specialized for overnight trading with gap analysis and momentum detection

### Performance Metrics
- **Execution Time**: Tracked for each analysis
- **Accuracy Tracking**: Historical accuracy measurement
- **Resource Usage**: Optimized for real-time analysis

### Security Features
- **Admin-only Access**: Requires admin authentication
- **Rate Limiting**: Prevents abuse of compute resources
- **Error Handling**: Graceful error management
- **Input Validation**: Secure parameter handling

## 🌐 API Documentation

### Authentication
All admin APIs require admin authentication via session.

### Request Format
```javascript
// Run Stock Recommender
POST /api/admin/ml_models/run_stock_recommender
FormData: {
    stock_category: "NSE_LARGE_CAP",
    min_confidence: 70
}

// Run BTST Analyzer  
POST /api/admin/ml_models/run_btst_analyzer
FormData: {
    stock_category: "BANKING",
    min_confidence: 70,
    btst_min_score: 75
}
```

### Response Format
```json
{
    "success": true,
    "result": {
        "id": "unique_result_id",
        "model_name": "advanced_stock_recommender",
        "total_analyzed": 10,
        "actionable_count": 3,
        "avg_confidence": 78.5,
        "execution_time_seconds": 45.2,
        "summary": "Found 3 actionable recommendations...",
        "results": [
            {
                "Symbol": "RELIANCE.NS",
                "Current Price": 2450.50,
                "Recommendation": "Buy",
                "Confidence (%)": 85,
                // ... more fields
            }
        ]
    }
}
```

## 🚨 Troubleshooting

### Common Issues

1. **"ML models are not available"**
   - Check if yfinance is installed: `pip install yfinance`
   - Verify model files exist in models/ directory
   - Run test_ml_models.py to diagnose

2. **"No stocks found for category"**
   - Check if stock categories are loaded
   - Run setup_ml_models.py to reload categories
   - Verify stocklist.xlsx format if using custom file

3. **Analysis taking too long**
   - Reduce number of stocks in category
   - Check internet connection for yfinance data fetch
   - Monitor server resources

4. **Database errors**
   - Run setup_ml_models.py to create/update tables
   - Check database permissions
   - Verify app.py database configuration

### Performance Tips
- Use smaller stock categories for faster analysis
- Run analysis during market hours for fresh data
- Monitor execution time in results
- Consider implementing caching for repeated analyses

## 📝 Future Enhancements

### Planned Features
- [ ] Model performance tracking dashboard
- [ ] Scheduled automated analysis
- [ ] Email alerts for high-confidence signals
- [ ] Portfolio simulation based on recommendations
- [ ] Integration with broker APIs for automated trading
- [ ] Machine learning model retraining pipeline
- [ ] Advanced visualization charts
- [ ] Sector-wise performance analytics

### Customization Options
- Add new technical indicators
- Create custom stock categories
- Implement additional ML models
- Add risk management rules
- Integrate alternative data sources

## 📞 Support

For technical support or feature requests, please:
1. Check the troubleshooting section above
2. Run the test scripts to isolate issues
3. Review server logs for detailed error messages
4. Ensure all dependencies are properly installed

---

**Note**: This feature requires admin privileges and is designed for professional stock analysis. Results should be used as part of a comprehensive investment strategy and not as sole trading decisions.
