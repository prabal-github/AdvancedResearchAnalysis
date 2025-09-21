# Investor Terminal

A comprehensive financial terminal interface for investors, providing real-time market data, portfolio management, watchlists, alerts, and command-line style trading tools.

## Features

### 🖥️ Terminal Interface
- **Command-line style interface** with auto-completion and command history
- **Real-time execution** of financial commands
- **Syntax highlighting** and error handling
- **Multiple session support** with session persistence

### 📊 Market Data & Analysis
- **Real-time stock quotes** and market data
- **Technical analysis** with RSI, moving averages, and volume indicators
- **Price history** and charting capabilities
- **Market overview** with major indices (S&P 500, Dow Jones, NASDAQ, VIX)

### 👁️ Watchlists
- **Multiple watchlists** for different investment strategies
- **Quick quote access** by clicking on symbols
- **Dynamic watchlist management** through terminal commands
- **Persistent storage** of watchlist data

### 💼 Portfolio Management
- **Multiple portfolio support** for different accounts or strategies
- **Real-time portfolio valuation** and P&L calculation
- **Holdings tracking** with quantity, average price, and current value
- **Performance metrics** and portfolio analytics

### 🔔 Price Alerts
- **Customizable price alerts** (above/below price, volume spikes)
- **Real-time alert monitoring** and notifications
- **Alert history** and management
- **Multi-condition alerts** for complex trading strategies

### 📈 Advanced Tools
- **Stock screener** with customizable criteria
- **News integration** for fundamental analysis
- **Risk analysis** and position sizing
- **Backtesting capabilities** for strategy validation

## Available Commands

### Basic Commands
```bash
help                    # Show all available commands
quote AAPL             # Get real-time quote for AAPL
watch TSLA             # Add TSLA to watchlist
portfolio              # Show portfolio summary
alerts                 # Show active alerts
clear                  # Clear terminal screen
```

### Analysis Commands
```bash
analyze MSFT           # Technical analysis for MSFT
news GOOGL             # Latest news for GOOGL
history AMZN 1y        # Price history for AMZN (1 year)
screener high_volume   # Stock screener for high volume stocks
```

### Advanced Commands
```bash
risk NVDA              # Risk analysis for NVDA position
backtest strategy1     # Backtest a trading strategy
portfolio rebalance    # Rebalance portfolio weights
alert AAPL above 150   # Create price alert for AAPL above $150
```

## Quick Start

### 1. Access the Terminal
Navigate to `/investor/terminal` after logging in as an investor.

### 2. Basic Usage
```bash
# Get help
help

# Check a stock quote
quote AAPL

# Add to watchlist
watch AAPL

# View portfolio
portfolio

# Set up an alert
alert AAPL above 150
```

### 3. Navigation
- **Arrow Up/Down**: Navigate command history
- **Tab**: Auto-complete commands
- **Escape**: Clear current input
- **Ctrl+K**: Clear terminal (shortcut)

## Database Schema

### InvestorTerminalSession
Tracks active terminal sessions for each investor.

```sql
- id: Session ID (primary key)
- investor_id: Foreign key to InvestorAccount
- session_name: Display name for the session
- description: Session description
- is_active: Whether session is currently active
- created_at: Session creation timestamp
- last_accessed: Last activity timestamp
- watchlist_symbols: JSON array of watched symbols
- preferred_timeframes: JSON array of preferred timeframes
- risk_settings: JSON object with risk parameters
```

### InvestorWatchlist
Manages investor watchlists.

```sql
- id: Watchlist ID (primary key)
- investor_id: Foreign key to InvestorAccount
- name: Watchlist name
- description: Watchlist description
- symbols: JSON array of stock symbols
- is_default: Whether this is the default watchlist
- created_at: Creation timestamp
- updated_at: Last update timestamp
```

### InvestorPortfolio
Tracks investor portfolios.

```sql
- id: Portfolio ID (primary key)
- investor_id: Foreign key to InvestorAccount
- name: Portfolio name
- description: Portfolio description
- total_value: Current total portfolio value
- total_invested: Total amount invested
- profit_loss: Current profit/loss amount
- profit_loss_percentage: Current profit/loss percentage
- is_active: Whether portfolio is active
- created_at: Creation timestamp
- updated_at: Last update timestamp
```

### InvestorPortfolioHolding
Individual holdings within portfolios.

```sql
- id: Holding ID (primary key)
- portfolio_id: Foreign key to InvestorPortfolio
- symbol: Stock symbol
- company_name: Company name
- quantity: Number of shares
- average_price: Average purchase price
- current_price: Current market price
- total_invested: Total amount invested in this holding
- current_value: Current value of the holding
- profit_loss: Current profit/loss for this holding
- profit_loss_percentage: Current profit/loss percentage
- last_updated: Last price update timestamp
```

### InvestorAlert
Price and condition alerts.

```sql
- id: Alert ID (primary key)
- investor_id: Foreign key to InvestorAccount
- symbol: Stock symbol to monitor
- alert_type: Type of alert (price_above, price_below, volume_spike, etc.)
- condition_value: Target price or threshold value
- message: Custom alert message
- is_active: Whether alert is currently active
- is_triggered: Whether alert has been triggered
- triggered_at: When alert was triggered
- created_at: Alert creation timestamp
```

### InvestorTerminalCommand
Command history for audit and replay.

```sql
- id: Command ID (primary key)
- session_id: Foreign key to InvestorTerminalSession
- command: Executed command
- response: Command response/output
- execution_time: Time taken to execute (seconds)
- status: Execution status (success, error, pending)
- created_at: Command execution timestamp
```

## API Endpoints

### Terminal Commands
- `POST /api/investor/terminal/command` - Execute terminal command

### Watchlist Management
- `GET /api/investor/watchlist` - Get all watchlists
- `POST /api/investor/watchlist` - Create new watchlist
- `PUT /api/investor/watchlist/<id>` - Update watchlist
- `DELETE /api/investor/watchlist/<id>` - Delete watchlist

### Portfolio Management
- `GET /api/investor/portfolio` - Get all portfolios
- `POST /api/investor/portfolio` - Create new portfolio
- `GET /api/investor/portfolio/<id>/holdings` - Get portfolio holdings
- `POST /api/investor/portfolio/<id>/holdings` - Add portfolio holding

### Alerts Management
- `GET /api/investor/alerts` - Get all alerts
- `POST /api/investor/alerts` - Create new alert
- `PUT /api/investor/alerts/<id>` - Update alert
- `DELETE /api/investor/alerts/<id>` - Delete alert

### Market Data
- `GET /api/investor/market_data/<symbol>` - Get market data for symbol
- `GET /api/investor/market_overview` - Get market overview

## Installation

### 1. Database Setup
Run the database creation script:
```bash
python create_investor_terminal_tables.py
```

### 2. Dependencies
Ensure the following Python packages are installed:
```bash
pip install yfinance pandas numpy flask flask-sqlalchemy
```

### 3. Configuration
The terminal uses the existing Flask application configuration. No additional configuration is required.

## Security Features

### Authentication & Authorization
- **Investor-only access** - Terminal requires investor role authentication
- **Session-based security** - Each session is tied to authenticated investor
- **Command validation** - All commands are validated before execution
- **Audit logging** - All commands and responses are logged for audit trails

### Data Protection
- **SQL injection prevention** - All database queries use parameterized statements
- **XSS protection** - All user inputs are sanitized
- **CSRF protection** - API endpoints use CSRF tokens
- **Rate limiting** - Command execution is rate-limited to prevent abuse

## Performance Optimization

### Caching
- **Market data caching** - Real-time data is cached for 30 seconds
- **Portfolio calculations** - Portfolio values are cached and updated periodically
- **Command results** - Frequently accessed data is cached

### Efficiency
- **Lazy loading** - Data is loaded only when needed
- **Pagination** - Large datasets are paginated
- **Async operations** - Non-blocking operations where possible
- **Database indexing** - Proper indexing on frequently queried columns

## Browser Compatibility

### Supported Browsers
- Chrome 70+
- Firefox 65+
- Safari 12+
- Edge 79+

### Mobile Support
- Responsive design for tablets and mobile devices
- Touch-friendly interface
- Optimized for mobile trading

## Future Enhancements

### Planned Features
- **Advanced charting** with TradingView integration
- **Options trading** support and analysis
- **Cryptocurrency** tracking and analysis
- **Social trading** features and copy trading
- **AI-powered insights** and recommendations
- **Real-time streaming** data and WebSocket support
- **Custom indicators** and strategy builder
- **Paper trading** mode for testing strategies

### Integration Roadmap
- **Broker API integration** for live trading
- **News API integration** for real-time news
- **Economic calendar** integration
- **Earnings calendar** and event tracking
- **ESG scoring** and sustainability metrics

## Support & Documentation

### Getting Help
1. Type `help` in the terminal for command reference
2. Check the documentation at `/docs/investor_terminal`
3. Contact support for technical assistance

### Troubleshooting
- **Command not found**: Check spelling and use `help` for available commands
- **Market data unavailable**: Check internet connection and market hours
- **Session expired**: Refresh the page and log in again
- **Performance issues**: Clear browser cache and disable extensions

### Known Limitations
- Market data is delayed by 15-20 minutes for free users
- Some advanced features require premium subscription
- Options data requires separate data feed subscription
- Real-time news requires external API integration

## Contributing

### Development Setup
1. Clone the repository
2. Set up virtual environment
3. Install dependencies: `pip install -r requirements.txt`
4. Run database migrations
5. Start development server

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests for new features
- Document all API endpoints

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Run end-to-end tests
python -m pytest tests/e2e/
```

## License

This investor terminal is part of the PredictRAM financial analysis platform. All rights reserved.

---

**Version**: 1.0.0  
**Last Updated**: September 2025  
**Maintainer**: PredictRAM Development Team
