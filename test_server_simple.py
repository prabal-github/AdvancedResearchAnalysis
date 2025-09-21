from flask import Flask, request, jsonify
import random
import json

app = Flask(__name__)

def analyze_stock_for_scenario(symbol, sector, scenario_title, scenario_type, scenario_description, six_month_return, volatility, stock_info):
    """Analyze a stock's potential based on scenario context"""
    
    # Convert inputs to lowercase for keyword matching
    scenario_text = (scenario_title + " " + scenario_description).lower()
    
    # Default values
    action = 'hold'
    expected_return = 0.0
    rationale = f"Neutral outlook based on scenario analysis"
    
    try:
        # Scenario-based analysis logic
        if 'interest rate' in scenario_text or 'rate hike' in scenario_text:
            if sector == 'banking':
                action = 'buy'
                expected_return = random.uniform(8, 15)
                rationale = "Banking sector benefits from higher interest rates through improved NIMs"
            elif sector == 'it':
                action = 'sell'
                expected_return = random.uniform(-12, -5)
                rationale = "IT sector faces headwinds from rate hikes and global slowdown"
            elif sector == 'auto':
                action = 'sell'
                expected_return = random.uniform(-10, -3)
                rationale = "Auto sector affected by higher financing costs"
        
        elif 'inflation' in scenario_text:
            if sector == 'fmcg':
                action = 'hold'
                expected_return = random.uniform(-2, 5)
                rationale = "FMCG companies have mixed impact from inflation"
            elif sector == 'metals':
                action = 'buy'
                expected_return = random.uniform(5, 12)
                rationale = "Metals benefit from inflationary environment"
            elif sector == 'pharma':
                action = 'buy'
                expected_return = random.uniform(3, 8)
                rationale = "Pharma is defensive with pricing power"
        
        elif 'oil' in scenario_text or 'crude' in scenario_text:
            if sector == 'oil_gas':
                if 'high' in scenario_text or 'spike' in scenario_text:
                    action = 'buy'
                    expected_return = random.uniform(10, 18)
                    rationale = "Oil companies benefit from higher crude prices"
                else:
                    action = 'sell'
                    expected_return = random.uniform(-8, -2)
                    rationale = "Oil companies face pressure from lower crude prices"
            elif sector == 'auto':
                action = 'sell'
                expected_return = random.uniform(-8, -3)
                rationale = "Auto sector faces margin pressure from higher oil prices"
        
        elif 'recession' in scenario_text or 'slowdown' in scenario_text:
            if sector == 'pharma':
                action = 'buy'
                expected_return = random.uniform(5, 10)
                rationale = "Pharma is defensive during economic slowdown"
            elif sector == 'fmcg':
                action = 'hold'
                expected_return = random.uniform(0, 5)
                rationale = "FMCG shows resilience during economic slowdown"
            else:
                action = 'sell'
                expected_return = random.uniform(-15, -5)
                rationale = f"{sector.title()} sector vulnerable during economic slowdown"
        
        # Adjust based on historical performance
        if six_month_return > 20:
            expected_return *= 0.7
            rationale += " (adjusted for recent strong performance)"
        elif six_month_return < -20:
            expected_return *= 1.2
            rationale += " (potential recovery play)"
        
        # Volatility adjustment
        if volatility > 5:
            rationale += f" (High volatility: {volatility:.1f}%)"
        
    except Exception as e:
        print(f"Error in scenario analysis for {symbol}: {e}")
    
    return action, round(expected_return, 1), rationale

def calculate_stock_confidence(symbol, sector, scenario_description, volatility):
    """Calculate confidence score for stock recommendation"""
    
    confidence = 50.0  # Base confidence
    
    # Sector relevance to scenario
    scenario_text = scenario_description.lower()
    
    if sector == 'banking' and ('interest' in scenario_text or 'rate' in scenario_text):
        confidence += 30
    elif sector == 'it' and ('global' in scenario_text or 'recession' in scenario_text):
        confidence += 25
    elif sector == 'pharma' and ('pandemic' in scenario_text or 'health' in scenario_text):
        confidence += 35
    elif sector == 'oil_gas' and ('oil' in scenario_text or 'crude' in scenario_text):
        confidence += 30
    
    # Volatility penalty
    if volatility > 5:
        confidence -= 15
    elif volatility > 3:
        confidence -= 10
    
    # Ensure confidence is within bounds
    confidence = max(10, min(95, confidence))
    
    return confidence

@app.route('/api/analyze_additional_stocks', methods=['POST'])
def analyze_additional_stocks():
    """Analyze additional stocks based on scenario context"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        symbols = data.get('symbols', [])
        scenario_id = data.get('scenario_id', '')
        scenario_title = data.get('scenario_title', '')
        scenario_type = data.get('scenario_type', '')
        scenario_description = data.get('scenario_description', '')
        
        if not symbols:
            return jsonify({"success": False, "error": "No stock symbols provided"}), 400
        
        if len(symbols) > 3:
            return jsonify({"success": False, "error": "Maximum 3 stocks allowed"}), 400
        
        print(f"Analyzing stocks: {symbols} for scenario: {scenario_title}")
        
        recommendations = []
        
        # Define sector mapping for better analysis
        sector_map = {
            'RELIANCE.NS': 'oil_gas', 'ONGC.NS': 'oil_gas', 'IOC.NS': 'oil_gas', 'BPCL.NS': 'oil_gas',
            'TCS.NS': 'it', 'INFY.NS': 'it', 'WIPRO.NS': 'it', 'HCLTECH.NS': 'it', 'TECHM.NS': 'it',
            'HDFCBANK.NS': 'banking', 'ICICIBANK.NS': 'banking', 'SBIN.NS': 'banking', 'KOTAKBANK.NS': 'banking', 'AXISBANK.NS': 'banking',
            'SUNPHARMA.NS': 'pharma', 'DRREDDY.NS': 'pharma', 'CIPLA.NS': 'pharma', 'BIOCON.NS': 'pharma',
            'MARUTI.NS': 'auto', 'HEROMOTOCO.NS': 'auto', 'TATAMOTORS.NS': 'auto', 'M&M.NS': 'auto',
            'TATASTEEL.NS': 'metals', 'JSWSTEEL.NS': 'metals', 'HINDALCO.NS': 'metals', 'VEDL.NS': 'metals',
            'HINDUNILVR.NS': 'fmcg', 'ITC.NS': 'fmcg', 'NESTLEIND.NS': 'fmcg', 'BAJAJFINSV.NS': 'finance'
        }
        
        for symbol in symbols:
            try:
                print(f"Processing symbol: {symbol}")
                
                # Get sector for the stock
                sector = sector_map.get(symbol, 'general')
                
                # Use simulated realistic data (since we can't rely on yfinance in this test)
                current_price = random.uniform(100, 3000)
                six_month_return = random.uniform(-30, 30)
                volatility = random.uniform(1, 6)
                
                # Analyze based on scenario context
                action, expected_return, rationale = analyze_stock_for_scenario(
                    symbol, sector, scenario_title, scenario_type, scenario_description,
                    six_month_return, volatility, {}
                )
                
                # Calculate confidence score
                confidence = calculate_stock_confidence(symbol, sector, scenario_description, volatility)
                
                recommendation = {
                    'ticker': symbol,
                    'sector': sector,
                    'action': action,
                    'expected_return': expected_return,
                    'rationale': rationale,
                    'confidence': f"{confidence:.1f}%",
                    'current_price': current_price,
                    'six_month_return': six_month_return,
                    'volatility': volatility
                }
                
                recommendations.append(recommendation)
                print(f"Successfully analyzed {symbol}: {action} with {expected_return}% expected return")
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                # Provide fallback recommendation
                sector = sector_map.get(symbol, 'unknown')
                confidence = calculate_stock_confidence(symbol, sector, scenario_description, 3.0)
                
                recommendation = {
                    'ticker': symbol,
                    'sector': sector,
                    'action': 'hold',
                    'expected_return': 0.0,
                    'rationale': f'Technical analysis unavailable. Based on {sector} sector outlook for given scenario.',
                    'confidence': f"{confidence:.1f}%",
                    'current_price': random.uniform(100, 3000),
                    'six_month_return': random.uniform(-15, 15),
                    'volatility': 3.0
                }
                recommendations.append(recommendation)
        
        print(f"Completed analysis for {len(recommendations)} stocks")
        
        return jsonify({
            "success": True,
            "recommendations": recommendations,
            "analyzed_count": len(recommendations),
            "scenario_context": {
                "title": scenario_title,
                "type": scenario_type,
                "description": scenario_description[:100] + "..." if len(scenario_description) > 100 else scenario_description
            }
        })
        
    except Exception as e:
        print(f"Error in analyze_additional_stocks: {e}")
        return jsonify({"success": False, "error": f"Analysis failed: {str(e)}"}), 500

@app.route('/test')
def test_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Additional Stocks API</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-5">
            <h2>Test Additional Stocks API</h2>
            <div class="mb-3">
                <label class="form-label">Stock Symbols (comma-separated):</label>
                <input type="text" class="form-control" id="stockInput" 
                       placeholder="RELIANCE.NS, TCS.NS, HDFCBANK.NS" 
                       value="RELIANCE.NS, TCS.NS, HDFCBANK.NS">
            </div>
            <button class="btn btn-primary" onclick="testAPI()">Test API</button>
            <div id="results" class="mt-4"></div>
        </div>
        
        <script>
        async function testAPI() {
            const symbols = document.getElementById('stockInput').value.split(',').map(s => s.trim());
            const resultsDiv = document.getElementById('results');
            
            try {
                const response = await fetch('/api/analyze_additional_stocks', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        symbols: symbols,
                        scenario_id: 'test_123',
                        scenario_title: 'Interest Rate Hike Scenario',
                        scenario_type: 'monetary_policy',
                        scenario_description: 'RBI increases interest rates by 50 basis points to combat inflation.'
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    let html = '<h4>Results:</h4>';
                    result.recommendations.forEach(rec => {
                        html += `
                            <div class="card mb-2">
                                <div class="card-body">
                                    <h6>${rec.ticker} (${rec.sector})</h6>
                                    <p><strong>Action:</strong> ${rec.action} | 
                                       <strong>Expected Return:</strong> ${rec.expected_return}% | 
                                       <strong>Confidence:</strong> ${rec.confidence}</p>
                                    <p><small>${rec.rationale}</small></p>
                                </div>
                            </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                } else {
                    resultsDiv.innerHTML = `<div class="alert alert-danger">Error: ${result.error}</div>`;
                }
            } catch (error) {
                resultsDiv.innerHTML = `<div class="alert alert-danger">Network Error: ${error.message}</div>`;
            }
        }
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("🚀 Starting test server on http://127.0.0.1:5009")
    print("📊 Test page: http://127.0.0.1:5009/test")
    app.run(debug=True, port=5009)
