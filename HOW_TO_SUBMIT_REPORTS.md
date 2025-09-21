# 📝 How to Submit Reports - Enhanced Research Quality Assessment System

## 🌐 Accessing the Application

1. **Open your web browser**
2. **Navigate to**: `http://localhost:5000`
3. You'll see the **Research QA Dashboard** main page

---

## 📊 Submitting a Report - Step by Step

### Method 1: Web Interface (Recommended)

1. **Click "Analyze New Report" Button**
   - Located in the top-right corner of the dashboard
   - Has a "+" icon and blue background

2. **Fill in the Report Form**
   - **Analyst Name**: Enter the name of the research analyst
   - **Report Text**: Paste or type the complete research report content
   - Stock tickers are automatically extracted from the text

3. **Click "Analyze Report"**
   - The system will process your report
   - You'll see a loading spinner during analysis
   - Results appear in a few seconds

4. **View Results**
   - After analysis, you get:
     - ✅ Success confirmation with Report ID
     - 🔗 "View Full Report" button
     - 📥 "Download Results" button

### Method 2: API Endpoint (For Developers)

```python
import requests
import json

# Prepare your data
data = {
    'analyst': 'Your Analyst Name',
    'text': 'Your complete research report text here...'
}

# Submit to the API
response = requests.post(
    'http://localhost:5000/analyze',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(data)
)

# Get the result
result = response.json()
print(f"Report ID: {result['report_id']}")
```

---

## 📋 Sample Report Format

Here's a sample report you can use to test the system:

```
RELIANCE INDUSTRIES LIMITED (RIL) - STRONG BUY
Price Target: ₹2,850 | Current: ₹2,435 | Upside: 17%

ANALYST CREDENTIALS: Sarah Johnson, CFA, SEBI Registration: INH000002345
RESEARCH METHODOLOGY: DCF model with 5-year projections, peer comparison analysis

EXECUTIVE SUMMARY:
RIL demonstrates exceptional fundamentals driven by digital transformation and renewable energy initiatives. 
Strong balance sheet, diversified revenue streams, and strategic execution position it as a top-tier investment.

FINANCIAL HIGHLIGHTS (Q3 FY24):
• Revenue: ₹2.35L Cr (+28% YoY) 
• EBITDA: ₹43,500 Cr (18.5% margin)
• Net Profit: ₹18,750 Cr (+23% YoY) 
• ROE: 13.2% 
• D/E: 0.31x

GEOPOLITICAL RISK ASSESSMENT:
Current trade war dynamics and sanctions on energy imports create both challenges and opportunities. 
RIL's diversified portfolio provides natural hedging against political instability. Government policy 
alignment in renewable energy and digital infrastructure positions the company favorably amid 
regulatory changes and international relations tensions.

COMPREHENSIVE RISK DISCLOSURE:
Market Risk: Oil price volatility (±15% impact on petrochemicals)
Liquidity Risk: Minimal given strong cash position (₹2.1L Cr)
Credit Risk: Low counterparty risk with diversified customer base
Operational Risk: Technology integration challenges in telecom
Regulatory Risk: Policy changes in energy and telecom sectors
Concentration Risk: Petrochemicals constitute 45% of EBITDA

ESG CONSIDERATIONS:
Environmental: Carbon neutrality target by 2035, ₹75,000 Cr green investment
Social: 50M+ digital users, rural connectivity initiatives
Governance: Board independence 60%, strong audit committee oversight

SEBI DISCLOSURES:
• No material conflict of interest 
• Price targets based on DCF methodology
• Analyst compensation not linked to specific recommendations
• Full research methodology available upon request
• Past performance disclaimers apply

CFA STANDARDS COMPLIANCE: Research follows CFA Institute guidelines
INTERNATIONAL PERSPECTIVE: Compared with global energy majors (ExxonMobil, Shell)
```

---

## 🎯 What Happens After Submission

### 1. **Automatic Processing**
- Ticker extraction (e.g., RELIANCE.NS, TCS.NS)
- Market data retrieval
- Text analysis and sentiment scoring

### 2. **Enhanced Analysis**
- ✅ **Geopolitical Risk Assessment** (10% weight)
- ✅ **SEBI Compliance Check** (8% weight)
- ✅ **Global Standards Validation**
- ✅ **Quality Metrics Calculation**

### 3. **Scoring Breakdown**
- 20% - Factual Accuracy
- 15% - Predictive Power
- 12% - Bias Assessment
- 12% - Originality
- 15% - Risk Disclosure
- 8% - Transparency
- **10% - Geopolitical Assessment** (NEW)
- **8% - SEBI Compliance** (NEW)

### 4. **Results Available**
- **Standard Report View**: Basic analysis and scores
- **Enhanced Analysis**: Detailed breakdown with all new features
- **Export Options**: JSON and text download

---

## 🔍 Viewing Your Results

### After Submission:
1. **Click "View Full Report"** from the success message
2. **Or** find your report in the dashboard table
3. **Click "Enhanced Analysis"** for detailed assessment

### Enhanced Analysis Includes:
- 🌍 Geopolitical risk evaluation
- ⚖️ SEBI compliance validation
- 🌐 Global standards assessment
- 🚨 Flagged alerts and issues
- 📋 Action items and recommendations
- 📊 Interactive charts and visualizations

---

## 📈 Using Compare Reports Feature

1. **Navigate to "Compare Reports"** from the top menu
2. **Select a ticker** from the dropdown
3. **Choose 2+ reports** to compare
4. **View side-by-side analysis** with:
   - Quality metrics comparison
   - Consensus analysis
   - Divergence detection
   - Interactive charts

---

## 💡 Pro Tips

### For Best Results:
- ✅ Include analyst credentials and SEBI registration
- ✅ Add comprehensive risk disclosures
- ✅ Include geopolitical considerations
- ✅ Mention ESG factors
- ✅ Use proper disclaimers and methodology

### Enhanced Features Detect:
- 🔍 **Geopolitical Keywords**: trade war, sanctions, political instability
- ⚖️ **SEBI Requirements**: disclosures, risk warnings, methodology
- 🌐 **Global Standards**: CFA compliance, ESG coverage, international perspective

---

## 🚀 Quick Start

1. **Open**: `http://localhost:5000`
2. **Click**: "Analyze New Report"
3. **Enter**: Analyst name and report text
4. **Submit**: Click "Analyze Report"
5. **View**: Results and enhanced analysis

Your Enhanced Research Quality Assessment System is ready to evaluate reports with cutting-edge compliance checking and global standards validation! 🎉
