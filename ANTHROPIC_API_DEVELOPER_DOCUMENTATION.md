# Anthropic API Integration - Developer Documentation

## 📋 **Table of Contents**

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [API Configuration](#api-configuration)
5. [Implementation Guide](#implementation-guide)
6. [Usage Examples](#usage-examples)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)
9. [Security Considerations](#security-considerations)
10. [Testing & Validation](#testing--validation)

---

## 🎯 **Overview**

This documentation provides step-by-step instructions for developers to integrate Anthropic Claude API into the PredictRAM ML platform for AI-powered run history analysis.

### **Features Provided:**
- **AI-Powered Analysis**: Claude Sonnet 3.5/3.7 integration for intelligent insights
- **Admin Configuration**: Web-based API key management
- **Multiple Analysis Types**: Comprehensive, Performance, and Trends analysis
- **AWS Deployment Ready**: Production-compatible implementation
- **Fallback Support**: Graceful degradation when AI is unavailable

### **System Requirements:**
- Python 3.8+
- Flask web framework
- PostgreSQL database
- Admin authentication system
- Anthropic API account

---

## 🔧 **Prerequisites**

### **1. Anthropic API Account**
```bash
# Get your API key from: https://console.anthropic.com/
# Account setup required with billing information
```

### **2. Python Dependencies**
```bash
pip install anthropic>=0.18.0
pip install flask
pip install sqlalchemy
pip install psycopg2-binary  # for PostgreSQL
```

### **3. Environment Setup**
```bash
# Optional: Set environment variable (alternative to UI configuration)
export ANTHROPIC_API_KEY="your_api_key_here"
# or
export CLAUDE_API_KEY="your_api_key_here"
```

---

## 🚀 **Installation & Setup**

### **Step 1: Install Anthropic Package**
```bash
# Install the official Anthropic Python SDK
pip install anthropic

# Verify installation
python -c "import anthropic; print('Anthropic SDK installed successfully')"
```

### **Step 2: Database Schema Update**
The system uses the existing `AdminAPIKey` table for secure storage:

```sql
-- Verify the table exists (should already be present)
SELECT * FROM admin_api_keys WHERE service_name = 'anthropic';

-- Table structure:
-- id (Primary Key)
-- service_name (String) - 'anthropic'
-- api_key (String) - Encrypted API key
-- description (String) - Description
-- is_active (Boolean) - Active status
-- test_result (String) - Last test result
-- last_tested (DateTime) - Last test timestamp
-- created_at (DateTime) - Creation timestamp
-- updated_at (DateTime) - Last update timestamp
-- created_by (String) - Admin user ID
```

### **Step 3: Code Integration**
The following components are already implemented in `app.py`:

1. **Claude Client Class** (Lines ~4980-5080)
2. **Analysis Route** (Lines ~46460+)
3. **Admin Configuration Route** (Lines ~28700+)
4. **Template Updates** (templates/published_catalog.html)

---

## ⚙️ **API Configuration**

### **Method 1: Web UI Configuration (Recommended)**

1. **Access Admin Panel:**
   ```
   URL: http://127.0.0.1:5008/published
   Requirement: Admin authentication required
   ```

2. **Configure API Key:**
   - Admin banner will appear at the top
   - Enter your Anthropic API key
   - Select preferred model (Sonnet 3.5 recommended)
   - Click "Save" to store securely
   - Click "Test" to validate connectivity

3. **Verification:**
   - Status will show: "🔑 API Key: Configured ✅"
   - Test result will display API validation status

### **Method 2: Environment Variable**
```bash
# Set environment variable before starting the application
export ANTHROPIC_API_KEY="sk-ant-api03-xxx"

# Start the application
python app.py
```

### **Method 3: Direct Database Insert**
```python
from app import app, db, AdminAPIKey
from datetime import datetime

with app.app_context():
    # Create new API key record
    api_key = AdminAPIKey(
        service_name='anthropic',
        api_key='your_api_key_here',
        description='Anthropic Claude API for AI-powered run history analysis',
        is_active=True,
        created_by='admin_user_id',
        created_at=datetime.utcnow()
    )
    
    db.session.add(api_key)
    db.session.commit()
    print("Anthropic API key configured successfully")
```

---

## 💻 **Implementation Guide**

### **Backend Implementation**

#### **1. Analysis Endpoint**
```python
@app.route('/api/published_models/<mid>/run_history_analysis', methods=['POST'])
def generate_run_history_analysis(mid):
    """Generate AI-powered run history analysis using Anthropic Claude"""
    
    # Authentication check
    if not (session.get('investor_id') or session.get('admin_id') or session.get('analyst_id')):
        return jsonify({'ok': False, 'error': 'Authentication required'}), 401
    
    # Get request parameters
    data = request.get_json() or {}
    model_preference = data.get('model', 'sonnet-3.5')
    analysis_type = data.get('analysis_type', 'comprehensive')
    limit = int(data.get('limit', 30))
    
    # Fetch run history data
    # ... (implemented in the code)
    
    # Generate AI analysis
    if anthropic_api_key and ANTHROPIC_AVAILABLE:
        client = anthropic.Anthropic(api_key=anthropic_api_key)
        message = client.messages.create(
            model=model_mapping[model_preference],
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}]
        )
        analysis_result = message.content[0].text
    
    return jsonify({
        'ok': True,
        'analysis': analysis_result,
        'context_data': context_data,
        'model_id': mid,
        'runs_analyzed': len(runs)
    })
```

#### **2. Admin Configuration Endpoint**
```python
@app.route('/api/admin/anthropic/config', methods=['GET', 'POST'])
@admin_required
def anthropic_admin_config():
    """Manage Anthropic AI configuration"""
    
    if request.method == 'GET':
        # Return current configuration
        anthropic_key = AdminAPIKey.query.filter_by(service_name='anthropic').first()
        return jsonify({
            'success': True,
            'config': {
                'api_key_configured': bool(anthropic_key and anthropic_key.api_key),
                'available_models': {
                    'sonnet-3.5': 'claude-3-5-sonnet-20241022',
                    'sonnet-4': 'claude-3-5-sonnet-20241022',
                    'sonnet-legacy': 'claude-3-sonnet-20240229'
                }
            }
        })
    
    elif request.method == 'POST':
        # Configure API key
        data = request.get_json()
        action = data.get('action', 'configure')
        
        if action == 'configure':
            api_key = data.get('api_key')
            # Test and save API key
            # ... (implemented in the code)
        
        return jsonify({'success': True, 'message': 'Configuration updated'})
```

### **Frontend Implementation**

#### **1. Analysis Dialog Enhancement**
```html
<!-- Enhanced UI controls in published_catalog.html -->
<div style="display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; margin-bottom:12px;">
    <div style="flex:1; min-width:160px;">
        <label for="analysisProvider">Provider</label>
        <select id="analysisProvider">
            <option value="ollama">Ollama (local)</option>
            <option value="anthropic">Anthropic Claude (AWS)</option>
        </select>
    </div>
    
    <div style="flex:1; min-width:180px;">
        <label for="analysisModel">Model</label>
        <select id="analysisModel">
            <option value="sonnet-3.5">Sonnet 3.5 (Recommended)</option>
            <option value="sonnet-4">Sonnet 4 (Future)</option>
            <option value="sonnet-legacy">Sonnet 3 (Legacy)</option>
        </select>
    </div>
    
    <div style="flex:1; min-width:160px;">
        <label for="analysisType">Analysis Type</label>
        <select id="analysisType">
            <option value="comprehensive">Comprehensive Report</option>
            <option value="performance">Performance Analysis</option>
            <option value="trends">Trends & Patterns</option>
        </select>
    </div>
</div>
```

#### **2. JavaScript Integration**
```javascript
const runAnalysis = async () => {
    const providerSel = document.getElementById('analysisProvider').value;
    const modelSel = document.getElementById('analysisModel').value.trim();
    const analysisType = document.getElementById('analysisType').value;
    
    if (providerSel === 'anthropic') {
        // Use new Anthropic-powered analysis endpoint
        const payload = {
            model: modelSel || 'sonnet-3.5',
            analysis_type: analysisType,
            limit: 30
        };
        
        const response = await fetch(`/api/published_models/${id}/run_history_analysis`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (result.ok) {
            displayAnalysis(result.analysis);
        }
    }
};
```

---

## 📖 **Usage Examples**

### **Example 1: Generate Comprehensive Analysis**
```bash
curl -X POST http://127.0.0.1:5008/api/published_models/MODEL_ID/run_history_analysis \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sonnet-3.5",
    "analysis_type": "comprehensive",
    "limit": 30
  }'
```

**Response:**
```json
{
  "ok": true,
  "analysis": {
    "content": "## Comprehensive Analysis - Stock Recommender Model\n\n### Executive Summary\nModel showing strong performance...",
    "model_used": "sonnet-3.5 (claude-3-5-sonnet-20241022)",
    "analysis_type": "comprehensive",
    "generated_at": "2025-01-09T14:30:45.123Z",
    "token_usage": 2847
  },
  "context_data": {
    "model_name": "Stock Recommender",
    "total_runs": 45,
    "performance_metrics": {
      "success_rate": 87.3,
      "avg_duration_ms": 1247
    }
  },
  "runs_analyzed": 45
}
```

### **Example 2: Performance Analysis Only**
```javascript
// Frontend JavaScript example
const analyzePerformance = async (modelId) => {
    const response = await fetch(`/api/published_models/${modelId}/run_history_analysis`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            model: 'sonnet-3.5',
            analysis_type: 'performance',
            limit: 20
        })
    });
    
    const result = await response.json();
    console.log('Performance Analysis:', result.analysis.content);
};
```

### **Example 3: Admin Configuration**
```javascript
// Configure Anthropic API key
const configureAnthropic = async (apiKey) => {
    const response = await fetch('/api/admin/anthropic/config', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            action: 'configure',
            api_key: apiKey
        })
    });
    
    const result = await response.json();
    if (result.success) {
        console.log('API key configured successfully');
    }
};
```

---

## 🌐 **Deployment**

### **Local Development**
```bash
# 1. Set environment variable (optional)
export ANTHROPIC_API_KEY="your_api_key"

# 2. Start the application
python app.py

# 3. Access the interface
# URL: http://127.0.0.1:5008/published
```

### **AWS EC2 Production**
```bash
# 1. Deploy your application to EC2
# 2. Set environment variables in production
echo "export ANTHROPIC_API_KEY='your_api_key'" >> ~/.bashrc
source ~/.bashrc

# 3. Configure via web interface
# URL: https://research.predictram.com/published

# 4. Verify deployment
curl -X GET https://research.predictram.com/api/admin/anthropic/config
```

### **Environment Variables for Production**
```bash
# Required for production deployment
export ANTHROPIC_API_KEY="sk-ant-api03-xxx"
export DATABASE_URL="postgresql://user:pass@host:port/db"
export SECRET_KEY="your_secret_key"
export FLASK_ENV="production"
```

---

## 🐛 **Troubleshooting**

### **Common Issues & Solutions**

#### **1. "Anthropic package not available"**
```bash
# Solution: Install the package
pip install anthropic>=0.18.0

# Verify installation
python -c "import anthropic; print('OK')"
```

#### **2. "API key validation failed"**
```bash
# Check API key format
# Should start with: sk-ant-api03-

# Test API key manually
python -c "
import anthropic
client = anthropic.Anthropic(api_key='your_key')
message = client.messages.create(
    model='claude-3-haiku-20240307',
    max_tokens=10,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print('API key is valid')
"
```

#### **3. "Authentication required"**
```bash
# Ensure you're logged in as admin/analyst/investor
# Check session data in browser developer tools
```

#### **4. "Analysis request failed"**
```bash
# Check server logs for detailed error
tail -f app.log

# Verify model availability
# Sonnet 3.5: claude-3-5-sonnet-20241022
# Sonnet 3: claude-3-sonnet-20240229
```

### **Debug Mode**
```python
# Enable debug logging for troubleshooting
import logging
logging.basicConfig(level=logging.DEBUG)

# Check API availability
from app import ANTHROPIC_AVAILABLE, ClaudeClient
print(f"Anthropic available: {ANTHROPIC_AVAILABLE}")

client = ClaudeClient()
print(f"Client available: {client.available}")
print(f"Available models: {client.model_options}")
```

---

## 🔒 **Security Considerations**

### **1. API Key Storage**
```python
# ✅ Secure storage in database
api_key = AdminAPIKey(
    service_name='anthropic',
    api_key=encrypt_api_key(raw_key),  # Encrypted storage
    is_active=True
)

# ❌ Don't store in plain text files
# ❌ Don't commit to version control
# ❌ Don't log API keys
```

### **2. Access Control**
```python
# Only admin users can configure API keys
@app.route('/api/admin/anthropic/config')
@admin_required  # Ensures admin authentication
def anthropic_admin_config():
    pass

# Analysis endpoint requires authentication
if not (investor_id or admin_id or analyst_id):
    return jsonify({'error': 'Authentication required'}), 401
```

### **3. Input Validation**
```python
# Validate model selection
valid_models = ['sonnet-3.5', 'sonnet-4', 'sonnet-legacy']
if model_preference not in valid_models:
    model_preference = 'sonnet-3.5'

# Validate analysis type
valid_types = ['comprehensive', 'performance', 'trends']
if analysis_type not in valid_types:
    analysis_type = 'comprehensive'

# Limit data exposure
limit = min(int(data.get('limit', 30)), 100)  # Max 100 runs
```

### **4. Rate Limiting**
```python
# Consider implementing rate limiting for API calls
# Example with Flask-Limiter:
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: session.get('user_id'),
    default_limits=["100 per hour"]
)

@app.route('/api/published_models/<mid>/run_history_analysis')
@limiter.limit("10 per minute")  # Limit AI analysis requests
def generate_run_history_analysis(mid):
    pass
```

---

## ✅ **Testing & Validation**

### **1. Automated Testing**
```python
# Run the validation script
python validate_anthropic_implementation.py

# Expected output:
# ✅ Route exists: /api/published_models/<mid>/run_history_analysis
# ✅ Route exists: /api/admin/anthropic/config
# ✅ Anthropic package available
# ✅ Claude client configured with models
# ✅ Template updated with Anthropic integration
```

### **2. Manual Testing**

#### **Step 1: Configuration Test**
```bash
# 1. Open http://127.0.0.1:5008/published
# 2. Login as admin
# 3. Configure API key in admin banner
# 4. Click "Test" button
# 5. Verify "✅ API key is valid and working" message
```

#### **Step 2: Analysis Test**
```bash
# 1. Navigate to published models page
# 2. Click any model's "Analysis" button
# 3. Select "Anthropic Claude (AWS)" as provider
# 4. Choose "Sonnet 3.5" model
# 5. Select "Comprehensive" analysis type
# 6. Click "Analyze AI"
# 7. Verify detailed AI analysis appears
```

#### **Step 3: API Endpoint Test**
```bash
# Test the endpoint directly
curl -X POST http://127.0.0.1:5008/api/published_models/1/run_history_analysis \
  -H "Content-Type: application/json" \
  -H "Cookie: session=your_session_cookie" \
  -d '{
    "model": "sonnet-3.5",
    "analysis_type": "performance",
    "limit": 10
  }'
```

### **3. Performance Testing**
```python
# Test response times
import time
import requests

start_time = time.time()
response = requests.post(
    'http://127.0.0.1:5008/api/published_models/1/run_history_analysis',
    json={'model': 'sonnet-3.5', 'analysis_type': 'comprehensive'},
    headers={'Content-Type': 'application/json'}
)
end_time = time.time()

print(f"Response time: {end_time - start_time:.2f} seconds")
print(f"Status code: {response.status_code}")
```

---

## 📚 **Additional Resources**

### **Anthropic Documentation**
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Claude Model Information](https://docs.anthropic.com/claude/docs/models-overview)
- [Python SDK Reference](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

### **Model Specifications**
```python
# Available models and their capabilities
ANTHROPIC_MODELS = {
    'claude-3-5-sonnet-20241022': {
        'name': 'Claude 3.5 Sonnet',
        'max_tokens': 4096,
        'context_window': 200000,
        'recommended_use': 'Complex analysis, detailed reports',
        'cost': 'Premium'
    },
    'claude-3-sonnet-20240229': {
        'name': 'Claude 3 Sonnet',
        'max_tokens': 4096,
        'context_window': 200000,
        'recommended_use': 'General analysis, stable performance',
        'cost': 'Standard'
    },
    'claude-3-haiku-20240307': {
        'name': 'Claude 3 Haiku',
        'max_tokens': 4096,
        'context_window': 200000,
        'recommended_use': 'Quick analysis, cost-effective',
        'cost': 'Economy'
    }
}
```

### **File Structure**
```
├── app.py                                    # Main application file
├── templates/
│   └── published_catalog.html               # Enhanced UI template
├── validate_anthropic_implementation.py     # Validation script
├── ANTHROPIC_RUN_HISTORY_ANALYSIS_IMPLEMENTATION.md
└── ANTHROPIC_API_DEVELOPER_DOCUMENTATION.md # This file
```

---

## 🎯 **Summary**

This developer documentation provides complete instructions for integrating Anthropic Claude API into the PredictRAM platform. The implementation includes:

- **Backend API endpoints** for AI-powered analysis
- **Admin configuration system** for secure key management
- **Enhanced UI components** for user interaction
- **Production deployment** compatibility
- **Security best practices** and error handling
- **Comprehensive testing** and validation tools

Follow this guide to successfully implement and deploy Anthropic AI integration in your development environment and production systems.

---

**Document Version**: 1.0  
**Last Updated**: January 9, 2025  
**Author**: AI Development Team  
**Compatibility**: Python 3.8+, Flask 2.0+, Anthropic SDK 0.18+
