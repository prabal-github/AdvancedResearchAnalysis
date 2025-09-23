# 🚀 Comprehensive API Documentation - Research Quality Application

## 📋 API Overview
This document provides detailed information about all available API endpoints for the Research Quality Application. All APIs return JSON responses and support CORS for cross-origin requests.

**Base URL:** `http://127.0.0.1:80`  
**API Version:** v1.0  
**Authentication:** Not required for current implementation  

---

## 🏠 1. Main Dashboard API

### GET `/api/main_dashboard`
**Description:** Retrieve main dashboard data with system metrics and analyst performance.

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "metrics": {
    "total_reports": 150,
    "avg_quality_score": 78.5,
    "top_analysts": [...],
    "metric_averages": {...},
    "recent_trends": [...]
  },
  "recent_reports": [...],
  "analyst_performance": [...],
  "system_health": {
    "total_reports": 150,
    "reports_today": 5,
    "reports_this_week": 23,
    "active_analysts": 8
  }
}
```

**Use Cases:**
- System monitoring dashboards
- Executive reporting
- Real-time metrics display

---

## 👤 2. Investor Dashboard API

### GET `/api/investor_dashboard`
**Description:** Get investor-focused data including queries, trends, and investment recommendations.

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "investor_queries": [...],
  "sector_interests": {
    "technology": 45,
    "banking": 32,
    "healthcare": 18
  },
  "query_trends": {...},
  "market_insights": {...},
  "investment_recommendations": [...],
  "portfolio_suggestions": {
    "conservative": ["HDFCBANK.NS", "ICICIBANK.NS"],
    "moderate": ["INFY.NS", "TCS.NS"],
    "aggressive": ["BHARTIARTL.NS", "MARUTI.NS"]
  }
}
```

**Use Cases:**
- Investor portals
- Portfolio management tools
- Market analysis applications

---

## 📊 3. Enhanced Analysis Reports API

### GET `/api/enhanced_analysis_reports`
### GET `/api/enhanced_analysis_reports/<ticker>`
**Description:** Retrieve enhanced analysis reports with quality metrics and market data.

**Query Parameters:**
- `limit` (int): Number of reports to return (default: 20)
- `offset` (int): Pagination offset (default: 0)
- `analyst` (string): Filter by analyst name
- `min_quality` (float): Minimum quality score filter

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "reports": [
    {
      "id": 123,
      "analyst": "John Doe",
      "ticker": "INFY.NS",
      "title": "Infosys Q3 Analysis",
      "created_at": "2025-07-21T10:30:00.000Z",
      "quality_metrics": {
        "composite_quality_score": 85.3,
        "factual_accuracy": 90.2,
        "predictive_power": 78.5,
        "bias_score": 15.2,
        "originality": 88.7,
        "risk_disclosure": 82.1,
        "transparency": 91.4
      },
      "plagiarism_analysis": {...},
      "market_data": {...},
      "content_summary": "...",
      "recommendations": [...],
      "key_insights": [...],
      "risk_factors": [...]
    }
  ],
  "pagination": {...},
  "statistics": {...},
  "filters": {...}
}
```

**Use Cases:**
- Report management systems
- Quality assessment tools
- Research databases

---

## 🛡️ 4. Admin Dashboard API

### GET `/api/admin_dashboard`
**Description:** Comprehensive admin dashboard with system metrics and performance analytics.

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "metrics": {
    "system_overview": {...},
    "quality_metrics": {...},
    "analyst_performance": [...],
    "system_health": {
      "database_status": "operational",
      "api_status": "operational",
      "ai_services": "operational",
      "plagiarism_detection": "operational"
    }
  },
  "recent_activity": [...],
  "alerts": [...]
}
```

**Use Cases:**
- System administration
- Performance monitoring
- Health checks

---

## 🔄 5. Compare Reports API

### POST `/api/compare_reports`
**Description:** Compare multiple reports for quality, similarity, and performance metrics.

**Request Body:**
```json
{
  "report_ids": [123, 124, 125]
}
```

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "reports": [...],
  "comparison_result": {...},
  "comparison_metrics": {
    "content_similarity": {...},
    "quality_variance": {...},
    "analyst_comparison": {...},
    "recommendation_alignment": {...}
  },
  "market_data": {...},
  "summary": {
    "total_reports_compared": 3,
    "best_quality_report": 123,
    "worst_quality_report": 125,
    "avg_quality_score": 78.5,
    "quality_range": {
      "min": 65.2,
      "max": 89.7
    }
  }
}
```

**Use Cases:**
- Comparative analysis tools
- Quality benchmarking
- Research validation

---

## 🤖 6. AI Research Assistant API

### GET `/api/ai_research_assistant`
**Description:** Get AI Research Assistant status and capabilities.

### POST `/api/ai_research_assistant`
**Description:** Process AI research queries with enhanced analysis.

**Request Body (POST):**
```json
{
  "query": "Latest analysis on INFY.NS"
}
```

**Response Structure (POST):**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "query": "Latest analysis on INFY.NS",
  "analysis": {
    "query_type": "stock_analysis",
    "keywords": ["latest", "analysis"],
    "tickers": ["INFY.NS"],
    "sectors": ["Technology"],
    "coverage_score": 0.85,
    "ai_response": "📊 **Stock Analysis for INFY.NS:** ...",
    "insights": [...],
    "recommendations": [...],
    "confidence": 0.92,
    "status": "answered",
    "market_data_available": true,
    "research_reports_found": 5
  },
  "processing_time": 2.1,
  "confidence_score": 0.92,
  "data_sources": ["Research Database", "Real-time Market Data", "Claude AI Analysis"]
}
```

**Use Cases:**
- AI-powered research tools
- Investment analysis platforms
- Query processing systems

---

## 📈 7. Admin Performance API

### GET `/api/admin/performance`
**Description:** Detailed performance analytics for administrators.

**Query Parameters:**
- `days` (int): Number of days to analyze (default: 30)

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "performance_data": {
    "overview": {...},
    "quality_trends": [...],
    "analyst_rankings": [...],
    "ticker_analysis": {...},
    "time_series_data": {...},
    "system_performance": {
      "database_health": {...},
      "api_metrics": {...},
      "quality_distribution": {
        "excellent": 45,
        "good": 67,
        "average": 28,
        "poor": 10
      }
    }
  },
  "summary": {...}
}
```

**Use Cases:**
- Performance analytics
- Trend analysis
- System optimization

---

## 👨‍💼 8. Analysts API

### GET `/api/analysts`
**Description:** Get all analysts overview and statistics.

### GET `/api/analysts/<analyst_name>`
**Description:** Get detailed information about a specific analyst.

**Response Structure (All Analysts):**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "analysts": [
    {
      "name": "John Doe",
      "total_reports": 25,
      "avg_quality_score": 85.3,
      "tickers_covered": 12,
      "last_report_date": "2025-07-21T10:30:00.000Z",
      "reports_this_week": 3
    }
  ],
  "summary": {
    "total_analysts": 8,
    "total_reports": 150,
    "avg_quality_across_all": 78.5,
    "most_active": "John Doe",
    "highest_quality": "Jane Smith"
  }
}
```

**Response Structure (Specific Analyst):**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "analyst": {
    "name": "John Doe",
    "statistics": {...},
    "performance_trends": [...],
    "recent_reports": [...],
    "top_tickers": [...],
    "quality_distribution": {
      "excellent": 15,
      "good": 8,
      "average": 2,
      "poor": 0
    }
  }
}
```

**Use Cases:**
- Analyst management systems
- Performance tracking
- Resource allocation

---

## 🎯 9. Analyst Performance API

### GET `/api/analyst/<analyst_name>/performance`
**Description:** Detailed performance analytics for individual analysts.

**Query Parameters:**
- `days` (int): Number of days to analyze (default: 90)

**Response Structure:**
```json
{
  "success": true,
  "timestamp": "2025-07-21T20:45:00.000Z",
  "performance": {
    "analyst_name": "John Doe",
    "summary": {...},
    "quality_metrics": {
      "avg_quality_score": 85.3,
      "quality_trend": "improving",
      "best_score": 95.2,
      "worst_score": 72.1,
      "consistency": 88.7,
      "detailed_metrics": {
        "factual_accuracy": {
          "average": 90.2,
          "trend": "improving"
        },
        "predictive_power": {
          "average": 78.5,
          "trend": "stable"
        }
      }
    },
    "productivity_metrics": {...},
    "coverage_analysis": {...},
    "time_series_data": [...],
    "comparative_analysis": {
      "rank_among_analysts": 2,
      "total_analysts": 8,
      "percentile": 87.5,
      "above_average": true
    }
  }
}
```

**Use Cases:**
- Individual performance reviews
- Compensation analysis
- Career development tracking

---

## 🔧 10. Existing Enhanced APIs (Previously Implemented)

### GET `/api/enhanced_knowledge_stats`
**Description:** Real-time knowledge base statistics with .NS stock focus.

### POST `/ai_query_analysis`
**Description:** Simple AI query analysis endpoint for testing.

### POST `/api/enhanced_ai_query`
**Description:** Advanced AI query processing with comprehensive analysis.

### GET `/api/metrics`
**Description:** Real-time quality metrics across all analysts.

### GET `/api/fundamental_analysis/<ticker>`
**Description:** Fundamental analysis data for specific tickers.

---

## 🛠 API Usage Examples

### JavaScript/Fetch Examples

```javascript
// Get main dashboard data
fetch('/api/main_dashboard')
  .then(response => response.json())
  .then(data => console.log(data));

// Post AI query
fetch('/api/ai_research_assistant', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'Latest on INFY.NS'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Get analyst performance
fetch('/api/analyst/John%20Doe/performance?days=60')
  .then(response => response.json())
  .then(data => console.log(data));
```

### Python/Requests Examples

```python
import requests
import json

base_url = 'http://127.0.0.1:80'

# Get enhanced analysis reports
response = requests.get(f'{base_url}/api/enhanced_analysis_reports', 
                       params={'limit': 10, 'min_quality': 75})
data = response.json()

# Compare reports
compare_data = {'report_ids': [123, 124, 125]}
response = requests.post(f'{base_url}/api/compare_reports', 
                        json=compare_data)
comparison = response.json()

# Get admin performance data
response = requests.get(f'{base_url}/api/admin/performance?days=30')
performance = response.json()
```

### cURL Examples

```bash
# Get investor dashboard
curl -X GET "http://127.0.0.1:80/api/investor_dashboard"

# Post AI research query
curl -X POST "http://127.0.0.1:80/api/ai_research_assistant" \
     -H "Content-Type: application/json" \
     -d '{"query": "Banking sector analysis"}'

# Get specific analyst data
curl -X GET "http://127.0.0.1:80/api/analysts/John%20Doe"
```

---

## 📊 Error Handling

All APIs use consistent error response format:

```json
{
  "success": false,
  "error": "Description of the error",
  "timestamp": "2025-07-21T20:45:00.000Z",
  "error_code": "API_ERROR_001" // Optional
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Resource Not Found
- `500`: Internal Server Error

---

## 🚀 Integration Guide

### 1. **Frontend Integration**
```javascript
class ApiClient {
  constructor(baseUrl = 'http://127.0.0.1:80') {
    this.baseUrl = baseUrl;
  }

  async getDashboard() {
    const response = await fetch(`${this.baseUrl}/api/main_dashboard`);
    return response.json();
  }

  async getAnalystPerformance(analyst, days = 90) {
    const response = await fetch(
      `${this.baseUrl}/api/analyst/${encodeURIComponent(analyst)}/performance?days=${days}`
    );
    return response.json();
  }
}
```

### 2. **Mobile App Integration**
```swift
// iOS Swift example
func fetchDashboardData() {
    let url = URL(string: "http://127.0.0.1:80/api/main_dashboard")!
    URLSession.shared.dataTask(with: url) { data, response, error in
        // Handle response
    }.resume()
}
```

### 3. **Third-Party Service Integration**
```python
class ResearchQualityAPI:
    def __init__(self, base_url="http://127.0.0.1:80"):
        self.base_url = base_url
    
    def get_reports(self, ticker=None, min_quality=0):
        url = f"{self.base_url}/api/enhanced_analysis_reports"
        if ticker:
            url += f"/{ticker}"
        
        params = {'min_quality': min_quality}
        response = requests.get(url, params=params)
        return response.json()
```

---

## 📋 API Testing

You can test all APIs using the provided endpoints. Here's a simple test script:

```python
import requests
import json

def test_all_apis():
    base_url = 'http://127.0.0.1:80'
    
    # Test each API endpoint
    endpoints = [
        '/api/main_dashboard',
        '/api/investor_dashboard', 
        '/api/enhanced_analysis_reports',
        '/api/admin_dashboard',
        '/api/analysts',
        '/api/admin/performance'
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f'{base_url}{endpoint}')
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

if __name__ == "__main__":
    test_all_apis()
```

---

## 🔐 Security Considerations

1. **Rate Limiting**: Consider implementing rate limiting for production use
2. **Authentication**: Add API key authentication for secure access
3. **CORS**: Configure CORS settings appropriately for your domain
4. **Input Validation**: All user inputs are validated and sanitized
5. **Error Handling**: Errors don't expose sensitive system information

---

## 📞 Support & Documentation

- **API Status**: All APIs are operational and tested ✅
- **Response Time**: Average response time < 2 seconds
- **Uptime**: 99.9% availability target
- **Support**: Contact development team for integration assistance

**Last Updated:** July 21, 2025  
**Version:** 1.0  
**Status:** Production Ready 🚀
