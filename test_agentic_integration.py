"""
Integration Guide and Test Script for Agentic AI System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json

def test_agentic_integration():
    """Test the agentic AI integration"""
    
    print("🤖 Testing Agentic AI Integration")
    print("=" * 50)
    
    try:
        # Test 1: Import core modules
        print("\n1. Testing imports...")
        from agentic_ai import AgentManager, InvestmentAgent
        from agentic_models import InvestmentAgent as AgentModel
        print("✅ Core modules imported successfully")
        
        # Test 2: Create agent manager
        print("\n2. Testing agent manager...")
        manager = AgentManager()
        print("✅ Agent manager created successfully")
        
        # Test 3: Create sample agent
        print("\n3. Testing agent creation...")
        sample_config = {
            'confidence_threshold': 0.7,
            'risk_tolerance': 0.5,
            'preferred_sectors': ['technology', 'banking']
        }
        agent = manager.create_agent_for_investor('test_investor_001', sample_config)
        print("✅ Sample agent created successfully")
        
        # Test 4: Test autonomous analysis
        print("\n4. Testing autonomous analysis...")
        analysis_result = agent.autonomous_analysis()
        print(f"✅ Analysis completed: {analysis_result['status']}")
        
        # Test 5: Test personalized recommendations
        print("\n5. Testing personalized recommendations...")
        recommendations = agent.personalized_recommendations("What stocks should I buy?")
        print(f"✅ Generated {len(recommendations)} recommendations")
        
        # Test 6: Test learning system
        print("\n6. Testing learning system...")
        learning_result = agent.learn_from_outcomes()
        print(f"✅ Learning completed: {learning_result['patterns_learned']} patterns learned")
        
        # Test 7: Test proactive monitoring
        print("\n7. Testing proactive monitoring...")
        alerts = agent.proactive_monitoring()
        print(f"✅ Generated {len(alerts)} alerts")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print("The Agentic AI system is ready for integration.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_integration_steps():
    """Print step-by-step integration instructions"""
    
    print("\n🔧 INTEGRATION STEPS")
    print("=" * 50)
    
    steps = [
        {
            "step": "1. Database Setup",
            "actions": [
                "Add agentic_models.py imports to your app.py",
                "Run db.create_all() to create new tables",
                "Verify tables are created in your database"
            ]
        },
        {
            "step": "2. Routes Integration",
            "actions": [
                "Import agentic_routes.py in your main app.py",
                "Add: from agentic_routes import register_agentic_routes",
                "Call: register_agentic_routes(app, db)",
                "Test API endpoints work properly"
            ]
        },
        {
            "step": "3. Template Integration",
            "actions": [
                "Copy agentic_dashboard.html to templates folder",
                "Update your main navigation to include AI Assistant link",
                "Test the dashboard loads properly"
            ]
        },
        {
            "step": "4. Background Processes",
            "actions": [
                "Set up background agent scheduler",
                "Configure periodic learning updates",
                "Set up alert notifications"
            ]
        },
        {
            "step": "5. Configuration",
            "actions": [
                "Configure agent parameters per investor",
                "Set up market data connections",
                "Configure notification systems"
            ]
        }
    ]
    
    for i, step_info in enumerate(steps, 1):
        print(f"\n{step_info['step']}:")
        for action in step_info['actions']:
            print(f"   • {action}")
    
    print(f"\n📝 INTEGRATION CODE SAMPLE")
    print("=" * 50)
    print("""
# In your main app.py, add these lines:

# 1. Import agentic components
from agentic_routes import register_agentic_routes
from agentic_models import (InvestmentAgent, AgentRecommendation, 
                           AgentAction, AgentAlert)

# 2. Register routes (after app creation)
register_agentic_routes(app, db)

# 3. Create database tables (after db initialization)
with app.app_context():
    db.create_all()

# 4. Add navigation link in your layout.html
# <a href="{{ url_for('agentic_dashboard') }}" class="nav-link">
#     🤖 AI Assistant
# </a>

# 5. Start background scheduler (optional)
from agentic_routes import schedule_agent_runs
schedule_agent_runs()
""")

def print_usage_examples():
    """Print usage examples for the agentic system"""
    
    print(f"\n📚 USAGE EXAMPLES")
    print("=" * 50)
    
    examples = [
        {
            "title": "Create an AI Agent",
            "code": """
from agentic_ai import AgentManager

manager = AgentManager()
agent = manager.create_agent_for_investor(
    investor_id='user_123',
    config={
        'confidence_threshold': 0.8,
        'risk_tolerance': 0.6,
        'preferred_sectors': ['technology', 'healthcare']
    }
)
"""
        },
        {
            "title": "Get Personalized Recommendations",
            "code": """
# Get recommendations for a specific query
recommendations = agent.personalized_recommendations(
    "What are the best technology stocks to buy this month?"
)

for rec in recommendations:
    print(f"{rec['ticker']}: {rec['recommendation']} "
          f"(Confidence: {rec['confidence']:.2f})")
"""
        },
        {
            "title": "Run Autonomous Analysis",
            "code": """
# Trigger autonomous analysis
result = agent.autonomous_analysis()

print(f"Analysis Status: {result['status']}")
print(f"Recommendations: {len(result['recommendations'])}")
print(f"Actions Taken: {len(result['actions_taken'])}")
"""
        },
        {
            "title": "Monitor Alerts",
            "code": """
# Get proactive alerts
alerts = agent.proactive_monitoring()

for alert in alerts:
    print(f"Alert: {alert['title']} ({alert['severity']})")
    print(f"Message: {alert['message']}")
"""
        },
        {
            "title": "API Usage",
            "code": """
# Using the REST API endpoints:

// Get recommendations
fetch('/api/agentic/recommendations?limit=5')
  .then(response => response.json())
  .then(data => console.log(data.recommendations));

// Trigger analysis
fetch('/api/agentic/autonomous_analysis', { method: 'POST' })
  .then(response => response.json())
  .then(data => console.log('Analysis:', data));

// Record feedback
fetch('/api/agentic/feedback', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    recommendation_id: 123,
    feedback: 'accepted'
  })
});
"""
        }
    ]
    
    for example in examples:
        print(f"\n{example['title']}:")
        print(example['code'])

def print_feature_overview():
    """Print overview of agentic AI features"""
    
    print(f"\n🚀 AGENTIC AI FEATURES")
    print("=" * 50)
    
    features = {
        "🤖 Autonomous Analysis": [
            "Continuous market monitoring",
            "Automatic research report analysis", 
            "Quality-filtered opportunity detection",
            "Risk-adjusted recommendation generation"
        ],
        "🧠 Machine Learning": [
            "Learn from recommendation outcomes",
            "Adapt strategies based on success patterns",
            "Improve confidence thresholds automatically",
            "Personalized parameter optimization"
        ],
        "🎯 Personalized Recommendations": [
            "Investor profile-based filtering",
            "Sector preference matching",
            "Risk tolerance alignment",
            "Investment horizon consideration"
        ],
        "🚨 Proactive Monitoring": [
            "Real-time market event detection",
            "Portfolio risk threshold monitoring",
            "Research update notifications",
            "Opportunity alert generation"
        ],
        "📊 Performance Tracking": [
            "Recommendation success rate monitoring",
            "Return attribution analysis",
            "Benchmark comparison",
            "Sharpe ratio calculation"
        ],
        "⚙️ Configuration Management": [
            "Customizable confidence thresholds",
            "Adjustable risk parameters",
            "Sector preference settings",
            "Learning rate configuration"
        ]
    }
    
    for feature_category, feature_list in features.items():
        print(f"\n{feature_category}:")
        for feature in feature_list:
            print(f"   ✓ {feature}")

def print_next_steps():
    """Print next steps for implementation"""
    
    print(f"\n🎯 NEXT STEPS")
    print("=" * 50)
    
    next_steps = [
        {
            "priority": "HIGH",
            "task": "Database Integration",
            "description": "Integrate agentic models with your existing database",
            "estimated_time": "2-4 hours"
        },
        {
            "priority": "HIGH", 
            "task": "Basic UI Integration",
            "description": "Add agentic dashboard to your application",
            "estimated_time": "3-5 hours"
        },
        {
            "priority": "MEDIUM",
            "task": "API Testing",
            "description": "Test all API endpoints and ensure proper functionality",
            "estimated_time": "2-3 hours"
        },
        {
            "priority": "MEDIUM",
            "task": "Background Processing",
            "description": "Set up scheduled agent runs and monitoring",
            "estimated_time": "1-2 hours"
        },
        {
            "priority": "LOW",
            "task": "Advanced Features",
            "description": "Implement portfolio tracking and advanced analytics",
            "estimated_time": "4-6 hours"
        }
    ]
    
    for step in next_steps:
        priority_color = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}[step["priority"]]
        print(f"\n{priority_color} {step['priority']} PRIORITY - {step['task']}")
        print(f"   Description: {step['description']}")
        print(f"   Estimated Time: {step['estimated_time']}")

if __name__ == "__main__":
    print("🤖 AGENTIC AI INVESTMENT SYSTEM")
    print("===============================")
    print("Complete implementation ready for integration!")
    
    # Run tests
    test_success = test_agentic_integration()
    
    if test_success:
        # Print integration guide
        print_integration_steps()
        print_usage_examples() 
        print_feature_overview()
        print_next_steps()
        
        print(f"\n✨ CONGRATULATIONS!")
        print("Your agentic AI system is ready!")
        print("Follow the integration steps above to get started.")
    else:
        print(f"\n❌ Please fix the test errors before integration.")
