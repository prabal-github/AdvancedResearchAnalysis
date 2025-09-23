import requests
import json

def test_ai_analysis():
    try:
        response = requests.get('http://127.0.0.1:80/api/investor/scripts/BTSTjson.py/ai_analysis')
        if response.status_code == 200:
            data = response.json()
            print('API Response Status:', response.status_code)
            print('Response Keys:', list(data.keys()))
            
            if 'analysis' in data:
                analysis = data['analysis']
                print('Analysis Keys:', list(analysis.keys()))
                
                # Check performance metrics
                if 'performance_metrics' in analysis:
                    metrics = analysis['performance_metrics']
                    print('\nPerformance Metrics:')
                    for key, value in metrics.items():
                        print(f'  {key}: {value}')
                
                # Check Claude analysis
                if 'claude_summary' in analysis:
                    print(f'\nClaude Summary Available: {bool(analysis["claude_summary"])}')
                    if analysis['claude_summary']:
                        print(f'Claude Summary Length: {len(analysis["claude_summary"])} chars')
                
                # Check AI insights
                if 'ai_insights' in analysis:
                    print(f'\nAI Insights Count: {len(analysis["ai_insights"])}')
                    for i, insight in enumerate(analysis['ai_insights'][:3]):  # Show first 3
                        print(f'  {i+1}. Type: {insight.get("type", "info")}, Title: {insight.get("title", "N/A")}')
            
            # Save full response for inspection
            with open('api_response_btst.json', 'w') as f:
                json.dump(data, f, indent=2)
            print('\nFull response saved to api_response_btst.json')
            return True
        else:
            print('API Error:', response.status_code, response.text)
            return False
    except Exception as e:
        print('Error:', str(e))
        return False

if __name__ == "__main__":
    test_ai_analysis()
