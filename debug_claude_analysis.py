from app import app, db, ScriptExecution, calculate_performance_metrics, generate_claude_analysis
from datetime import datetime, timedelta

def debug_claude_analysis():
    with app.app_context():
        # Get BTSTjson.py executions
        executions = ScriptExecution.query.filter(
            ScriptExecution.script_name == 'BTSTjson.py',
            ScriptExecution.status == 'success',
            ScriptExecution.timestamp >= datetime.utcnow() - timedelta(days=90)
        ).order_by(ScriptExecution.timestamp.desc()).all()
        
        print(f"Found {len(executions)} executions for BTSTjson.py")
        
        if executions:
            performance_metrics = calculate_performance_metrics(executions)
            print("Performance metrics calculated successfully")
            
            # Test generate_claude_analysis
            try:
                claude_analysis = generate_claude_analysis('BTSTjson.py', executions, performance_metrics)
                print(f"Claude analysis successful!")
                print(f"Keys: {list(claude_analysis.keys())}")
                print(f"Insights count: {len(claude_analysis.get('insights', []))}")
                
                if claude_analysis.get('insights'):
                    print("First few insights:")
                    for i, insight in enumerate(claude_analysis['insights'][:3]):
                        print(f"  {i+1}. {insight.get('type', 'info')}: {insight.get('title', 'N/A')}")
                        print(f"     {insight.get('description', 'N/A')[:100]}...")
                        
                # Save full analysis for inspection
                import json
                with open('debug_claude_analysis.json', 'w') as f:
                    json.dump(claude_analysis, f, indent=2)
                print("Full analysis saved to debug_claude_analysis.json")
                
            except Exception as e:
                print(f"Error in generate_claude_analysis: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("No executions found")

if __name__ == "__main__":
    debug_claude_analysis()
