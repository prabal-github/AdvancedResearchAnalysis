# SQLite Database Integration Guide for ML Class and Catalog System

## Overview

This document explains how to integrate the comprehensive SQLite database with your existing Flask application for the ML Class and catalog system.

## Files Created

### 1. Database Schema and Setup
- **`create_simple_ml_ai_database.py`** - Creates the SQLite database with full schema
- **`ml_ai_system.db`** - The SQLite database file (created after running the script)

### 2. Database Integration Layer  
- **`ml_ai_database.py`** - Python module providing database connectivity and methods
- **`flask_db_integration.py`** - Example Flask routes showing database integration

### 3. Documentation
- **`DATABASE_INTEGRATION_GUIDE.md`** - This guide

## Database Schema

The database includes 14 tables covering all aspects of the ML/AI system:

### Core Tables
1. **`users`** - User accounts and authentication
2. **`ai_agents`** - Registry of AI agents with metadata
3. **`ml_models`** - Registry of ML models with performance metrics
4. **`portfolios`** - User portfolio management
5. **`portfolio_holdings`** - Individual stock holdings
6. **`user_subscriptions`** - User subscriptions to agents/models

### Analytics Tables
7. **`agent_executions`** - Complete execution history for agents
8. **`model_predictions`** - Model prediction history and accuracy tracking
9. **`risk_analytics`** - Portfolio risk metrics (VaR, volatility, etc.)
10. **`performance_analytics`** - Portfolio performance metrics
11. **`market_data`** - Cached market data from multiple sources

### System Tables
12. **`system_config`** - System configuration management
13. **`notifications`** - User notifications
14. **`chat_history`** - ML Class chat conversation history

## Quick Start

### 1. Create the Database

```bash
python create_simple_ml_ai_database.py
```

This creates `ml_ai_system.db` with:
- ✅ 12 AI Agents (from both catalog and ML Class)
- ✅ 10 ML Models (from both systems) 
- ✅ Complete schema with indexes
- ✅ Sample data and configurations

### 2. Test Database Connection

```bash
python ml_ai_database.py
```

Expected output:
```
✅ Database connection successful!
   🤖 AI Agents: 12
   🧠 ML Models: 10
   📋 Test subscriptions: 1 agents, 1 models
```

### 3. Integration with Your Flask App

Add this to your `app.py`:

```python
# Import the database integration
from ml_ai_database import get_db, get_available_ai_agents_from_db, get_available_ml_models_from_db
from flask_db_integration import register_database_routes

# Register database routes
register_database_routes(app)

# Modified ML Class route using database
@app.route('/vs_terminal_MLClass_with_db')
def vs_terminal_mlclass_with_database():
    try:
        # Get user info from session
        user_id = session.get('user_id', 1)  # Default for testing
        user_tier = session.get('account_type', 'M')
        
        # Get data from database instead of hardcoded functions
        db = get_db()
        subscriptions = db.get_user_subscriptions(user_id)
        available_agents = db.get_agents_for_tier(user_tier)
        available_models = db.get_models_for_tier(user_tier)
        
        return render_template('vs_terminal_mlclass.html',
                             subscribed_agents=subscriptions['agents'],
                             subscribed_models=subscriptions['models'],
                             available_agents=available_agents,
                             available_models=available_models,
                             user_tier=user_tier)
    except Exception as e:
        return f"Database error: {e}", 500
```

## API Endpoints

The integration provides these new API endpoints:

### Agent and Model Management
- `GET /db/api/db/agents` - Get all AI agents (with tier filtering)
- `GET /db/api/db/models` - Get all ML models (with tier filtering)
- `GET /db/api/db/agents?tier=M` - Get agents for specific tier

### Subscription Management
- `GET /db/api/db/subscriptions/<user_id>` - Get user subscriptions
- `POST /db/api/db/subscribe` - Add subscription
- `POST /db/api/db/unsubscribe` - Remove subscription

### Execution and Logging
- `POST /db/api/db/execute_agent` - Execute agent with database logging
- `POST /db/api/db/predict_model` - Run model prediction with logging
- `GET /db/api/db/execution_history/<user_id>` - Get execution history
- `GET /db/api/db/prediction_history/<user_id>` - Get prediction history

### System Management
- `GET /db/api/db/status` - Database status and statistics
- `GET /db/api/db/config/<key>` - Get system configuration
- `GET /db/api/db/notifications/<user_id>` - Get user notifications

## Usage Examples

### 1. Get User's Subscribed Agents

```python
from ml_ai_database import get_db

db = get_db()
user_id = 1
subscriptions = db.get_user_subscriptions(user_id)

print(f"User has {len(subscriptions['agents'])} subscribed agents")
print(f"User has {len(subscriptions['models'])} subscribed models")
```

### 2. Add a Subscription

```python
# Add subscription via API
import requests

response = requests.post('http://localhost:5008/db/api/db/subscribe', json={
    'user_id': 1,
    'item_type': 'agent',
    'item_id': 'portfolio_risk',
    'tier': 'M'
})

print(response.json())
```

### 3. Execute Agent with Logging

```python
# Execute agent and automatically log to database
response = requests.post('http://localhost:5008/db/api/db/execute_agent', json={
    'user_id': 1,
    'agent_id': 'portfolio_risk',
    'portfolio_id': 1,
    'input_params': {'symbols': ['RELIANCE', 'TCS']}
})

result = response.json()
print(f"Execution ID: {result['execution_id']}")
print(f"Results: {result['result']}")
```

### 4. Get Execution History

```python
# Get recent executions for a user
response = requests.get('http://localhost:5008/db/api/db/execution_history/1?limit=5')
history = response.json()

print(f"Found {history['count']} recent executions")
for execution in history['executions']:
    print(f"- {execution['agent_id']}: {execution['execution_status']}")
```

## Migration from Current System

### Step 1: Update Route Functions

Replace your existing hardcoded agent/model functions:

**Before:**
```python
def get_available_ai_agents():
    return [
        {'id': 'portfolio_risk', 'name': 'Portfolio Risk Agent', ...},
        # hardcoded list
    ]
```

**After:**
```python
def get_available_ai_agents():
    from ml_ai_database import get_db
    db = get_db()
    return db.get_all_ai_agents()
```

### Step 2: Update Subscription Logic

**Before:**
```python
# JSON file based subscriptions
with open('user_subscriptions.json', 'r') as f:
    subscriptions = json.load(f)
```

**After:**
```python
# Database based subscriptions
from ml_ai_database import get_db
db = get_db()
subscriptions = db.get_user_subscriptions(user_id)
```

### Step 3: Add Execution Logging

Enhance your agent execution with database logging:

```python
def execute_portfolio_risk_agent(user_id, params):
    start_time = time.time()
    
    # Your existing agent logic
    results = run_risk_analysis(params)
    
    # Log to database
    execution_time_ms = int((time.time() - start_time) * 1000)
    db = get_db()
    db.log_agent_execution(
        user_id=user_id,
        agent_id='portfolio_risk',
        input_params=params,
        result_data=results,
        execution_time_ms=execution_time_ms,
        confidence_score=results.get('confidence')
    )
    
    return results
```

## Benefits of Database Integration

### 1. **Persistent Data Storage**
- No more JSON file dependencies
- Reliable data persistence across application restarts
- ACID compliance for data integrity

### 2. **Performance Tracking**
- Complete audit trail of all agent executions
- Model prediction accuracy tracking over time
- Performance metrics and optimization insights

### 3. **Scalability**
- SQLite handles concurrent reads efficiently
- Easy migration to PostgreSQL/MySQL if needed
- Indexed queries for fast data retrieval

### 4. **Analytics Capabilities**
- Historical analysis of user behavior
- Agent/model performance comparisons
- Portfolio analytics and risk tracking

### 5. **User Experience**
- Faster subscription management
- Real-time execution history
- Personalized notifications and recommendations

## Configuration Options

### Database Location
```python
# Default: current directory
db = MLAIDatabase()

# Custom location
db = MLAIDatabase("/path/to/your/database.db")
```

### Connection Pooling
The database module uses context managers for automatic connection management:

```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    # Your database operations
    # Connection automatically closed
```

## Troubleshooting

### Database Not Found
```bash
# Recreate database
python create_simple_ml_ai_database.py
```

### Permission Errors
```bash
# Check file permissions
ls -la ml_ai_system.db

# Fix permissions if needed (Unix/Linux)
chmod 664 ml_ai_system.db
```

### Import Errors
```python
# Make sure the module is in your Python path
import sys
sys.path.append('/path/to/your/project')
from ml_ai_database import get_db
```

## Next Steps

1. **Test Integration**: Run the database creation and test scripts
2. **Update Routes**: Modify your existing Flask routes to use database functions
3. **Add Logging**: Enhance your agent/model execution with database logging
4. **Monitor Performance**: Use the analytics tables to track system performance
5. **Scale Up**: Consider migrating to PostgreSQL for production use

## Support

For issues or questions about the database integration:

1. Check the test functions in `ml_ai_database.py`
2. Review the example routes in `flask_db_integration.py`  
3. Use the `/db/api/db/status` endpoint to verify database connectivity
4. Check the database file permissions and path

The database integration provides a solid foundation for scaling your ML/AI system while maintaining all existing functionality.
