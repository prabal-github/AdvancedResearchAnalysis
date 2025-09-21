"""
Integration Script for Agentic AI System
Run this script to add agentic AI functionality to your existing app.py
"""

import os
import re
from datetime import datetime

def integrate_agentic_ai():
    """Integrate agentic AI system with existing app.py"""
    
    app_py_path = "app.py"
    
    if not os.path.exists(app_py_path):
        print("❌ app.py not found in current directory")
        return False
    
    try:
        # Read current app.py
        with open(app_py_path, 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        # Backup original file
        backup_path = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        print(f"✅ Created backup: {backup_path}")
        
        # Check if agentic imports already exist
        if 'agentic_routes' in app_content:
            print("⚠️  Agentic AI imports already exist in app.py")
            return True
        
        # Add imports after existing imports
        import_section = """
# Agentic AI System Imports
try:
    from agentic_routes import register_agentic_routes
    from agentic_models import InvestmentAgent, AgentRecommendation, AgentAction, AgentAlert
    AGENTIC_AI_AVAILABLE = True
    print("✅ Agentic AI system loaded successfully")
except ImportError as e:
    print(f"⚠️  Agentic AI system not available: {e}")
    AGENTIC_AI_AVAILABLE = False
"""
        
        # Find a good place to insert imports (after other imports)
        if 'from flask_sqlalchemy import SQLAlchemy' in app_content:
            app_content = app_content.replace(
                'from flask_sqlalchemy import SQLAlchemy',
                'from flask_sqlalchemy import SQLAlchemy' + import_section
            )
        else:
            # Insert after Flask imports
            flask_import_pattern = r'from flask import[^\\n]*\\n'
            match = re.search(flask_import_pattern, app_content)
            if match:
                insert_pos = match.end()
                app_content = app_content[:insert_pos] + import_section + app_content[insert_pos:]
        
        # Add route registration after app creation
        route_registration = """
# Register Agentic AI Routes
if AGENTIC_AI_AVAILABLE:
    try:
        register_agentic_routes(app, db)
        print("✅ Agentic AI routes registered successfully")
    except Exception as e:
        print(f"❌ Failed to register agentic AI routes: {e}")
"""
        
        # Find where to insert route registration (after db.create_all() or similar)
        if 'db.create_all()' in app_content:
            app_content = app_content.replace(
                'db.create_all()',
                'db.create_all()' + route_registration
            )
        elif 'if __name__ == "__main__":' in app_content:
            app_content = app_content.replace(
                'if __name__ == "__main__":',
                route_registration + '\\nif __name__ == "__main__":'
            )
        else:
            # Add at end of file before main block
            app_content += route_registration
        
        # Write updated app.py
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(app_content)
        
        print("✅ Successfully integrated agentic AI system into app.py")
        return True
        
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False

def create_database_tables():
    """Create database tables for agentic AI system"""
    
    create_tables_script = """
-- Agentic AI Database Tables

-- Investment Agents Table
CREATE TABLE IF NOT EXISTS investment_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id VARCHAR(50) NOT NULL,
    agent_name VARCHAR(100) DEFAULT 'AI Investment Advisor',
    config TEXT,  -- JSON configuration
    total_recommendations INTEGER DEFAULT 0,
    successful_recommendations INTEGER DEFAULT 0,
    accuracy_rate REAL DEFAULT 0.0,
    total_return REAL DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE,
    last_analysis_time DATETIME,
    last_learning_update DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Agent Actions Table
CREATE TABLE IF NOT EXISTS agent_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    ticker VARCHAR(20),
    action_data TEXT,  -- JSON data
    confidence_score REAL,
    risk_level VARCHAR(20),
    expected_return REAL,
    execution_status VARCHAR(20) DEFAULT 'pending',
    outcome_measured BOOLEAN DEFAULT FALSE,
    actual_return REAL,
    success BOOLEAN,
    market_context TEXT,  -- JSON data
    research_report_id VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    executed_at DATETIME,
    outcome_measured_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES investment_agents (id)
);

-- Agent Recommendations Table
CREATE TABLE IF NOT EXISTS agent_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    ticker VARCHAR(20) NOT NULL,
    recommendation_type VARCHAR(20) NOT NULL,
    target_price REAL,
    current_price REAL,
    confidence_score REAL NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    expected_return REAL,
    time_horizon VARCHAR(20),
    reasoning TEXT,  -- JSON data
    research_quality_score REAL,
    analyst_track_record REAL,
    market_conditions_score REAL,
    technical_score REAL,
    status VARCHAR(20) DEFAULT 'active',
    investor_response VARCHAR(20),
    outcome_return REAL,
    outcome_success BOOLEAN,
    based_on_report_id VARCHAR(50),
    analyst_name VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    closed_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES investment_agents (id)
);

-- Agent Learning Table
CREATE TABLE IF NOT EXISTS agent_learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data TEXT NOT NULL,  -- JSON data
    recommendation_id INTEGER,
    action_id INTEGER,
    confidence_in_pattern REAL DEFAULT 0.5,
    times_pattern_seen INTEGER DEFAULT 1,
    success_rate_with_pattern REAL DEFAULT 0.0,
    learning_source VARCHAR(50),
    importance_score REAL DEFAULT 0.5,
    config_changes_applied TEXT,  -- JSON data
    improvement_measured REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_applied DATETIME,
    FOREIGN KEY (agent_id) REFERENCES investment_agents (id),
    FOREIGN KEY (recommendation_id) REFERENCES agent_recommendations (id),
    FOREIGN KEY (action_id) REFERENCES agent_actions (id)
);

-- Agent Alerts Table
CREATE TABLE IF NOT EXISTS agent_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    ticker VARCHAR(20),
    sector VARCHAR(50),
    alert_data TEXT,  -- JSON data
    action_required BOOLEAN DEFAULT FALSE,
    suggested_action VARCHAR(100),
    urgency_level VARCHAR(20) DEFAULT 'NORMAL',
    status VARCHAR(20) DEFAULT 'active',
    investor_response VARCHAR(20),
    response_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES investment_agents (id)
);

-- Agent Performance Metrics Table
CREATE TABLE IF NOT EXISTS agent_performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    metric_date DATETIME NOT NULL,
    period_type VARCHAR(20) NOT NULL,
    recommendations_made INTEGER DEFAULT 0,
    recommendations_successful INTEGER DEFAULT 0,
    accuracy_rate REAL DEFAULT 0.0,
    total_return REAL DEFAULT 0.0,
    average_return_per_recommendation REAL DEFAULT 0.0,
    best_performing_recommendation_return REAL DEFAULT 0.0,
    worst_performing_recommendation_return REAL DEFAULT 0.0,
    portfolio_volatility REAL DEFAULT 0.0,
    sharpe_ratio REAL DEFAULT 0.0,
    max_drawdown REAL DEFAULT 0.0,
    response_time_avg REAL DEFAULT 0.0,
    learning_iterations INTEGER DEFAULT 0,
    config_adjustments INTEGER DEFAULT 0,
    vs_market_performance REAL DEFAULT 0.0,
    vs_human_analyst_performance REAL DEFAULT 0.0,
    investor_satisfaction_score REAL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES investment_agents (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_investment_agents_investor_id ON investment_agents(investor_id);
CREATE INDEX IF NOT EXISTS idx_agent_actions_agent_id ON agent_actions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_recommendations_agent_id ON agent_recommendations(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_recommendations_ticker ON agent_recommendations(ticker);
CREATE INDEX IF NOT EXISTS idx_agent_alerts_agent_id ON agent_alerts(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_alerts_status ON agent_alerts(status);
"""
    
    with open('create_agentic_tables.sql', 'w', encoding='utf-8') as f:
        f.write(create_tables_script)
    
    print("✅ Created create_agentic_tables.sql")
    print("   Run this SQL script in your database to create the required tables")

def check_integration_status():
    """Check the current integration status"""
    
    print("🔍 INTEGRATION STATUS CHECK")
    print("=" * 50)
    
    files_to_check = [
        "agentic_ai.py",
        "agentic_models.py", 
        "agentic_routes.py",
        "templates/agentic_dashboard.html",
        "test_agentic_integration.py"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing")
            all_files_exist = False
    
    # Check app.py integration
    if os.path.exists("app.py"):
        with open("app.py", 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'agentic_routes' in content:
            print("✅ app.py - Agentic AI integrated")
        else:
            print("⚠️  app.py - Not integrated yet")
    else:
        print("❌ app.py - Not found")
    
    # Check templates
    admin_template_updated = False
    investor_template_updated = False
    
    if os.path.exists("templates/admin_dashboard.html"):
        with open("templates/admin_dashboard.html", 'r', encoding='utf-8') as f:
            content = f.read()
            if 'AI Assistant' in content or 'agentic_ai' in content:
                admin_template_updated = True
    
    if os.path.exists("templates/investor_dashboard.html"):
        with open("templates/investor_dashboard.html", 'r', encoding='utf-8') as f:
            content = f.read()
            if 'AI Assistant' in content or 'agentic_ai' in content:
                investor_template_updated = True
    
    print(f"{'✅' if admin_template_updated else '⚠️ '} Admin dashboard - AI Assistant link {'added' if admin_template_updated else 'not added'}")
    print(f"{'✅' if investor_template_updated else '⚠️ '} Investor dashboard - AI Assistant link {'added' if investor_template_updated else 'not added'}")
    
    return all_files_exist

def print_access_instructions():
    """Print instructions for accessing the agentic dashboard"""
    
    print("\\n🚀 HOW TO ACCESS AGENTIC AI DASHBOARD")
    print("=" * 50)
    
    print("\\n📍 DASHBOARD ACCESS URLS:")
    print("• Main Dashboard: http://localhost:5000/agentic_ai")
    print("• API Base URL: http://localhost:5000/api/agentic/")
    
    print("\\n🔗 NAVIGATION LINKS ADDED:")
    print("• Admin Dashboard: 'AI Assistant' button (yellow/warning style)")
    print("• Investor Dashboard: 'AI Assistant' button (yellow/warning style)")
    
    print("\\n🔧 API ENDPOINTS AVAILABLE:")
    endpoints = [
        "GET /agentic_ai - Main dashboard",
        "POST /api/agentic/autonomous_analysis - Trigger analysis", 
        "GET /api/agentic/recommendations - Get recommendations",
        "GET /api/agentic/alerts - Get alerts",
        "POST /api/agentic/learn - Trigger learning",
        "GET/POST /api/agentic/config - Manage configuration",
        "POST /api/agentic/feedback - Record feedback"
    ]
    
    for endpoint in endpoints:
        print(f"   • {endpoint}")
    
    print("\\n⚙️  INTEGRATION STEPS:")
    steps = [
        "1. Run integrate_agentic_ai() to update app.py",
        "2. Create database tables using the SQL script",
        "3. Restart your Flask application", 
        "4. Visit /agentic_ai to see the dashboard",
        "5. Click 'AI Assistant' buttons in admin/investor dashboards"
    ]
    
    for step in steps:
        print(f"   {step}")

if __name__ == "__main__":
    print("🤖 AGENTIC AI INTEGRATION SCRIPT")
    print("=" * 40)
    
    # Check current status
    all_files_ready = check_integration_status()
    
    if all_files_ready:
        print("\\n✅ All agentic AI files are present!")
        
        # Ask user if they want to integrate
        response = input("\\n🤔 Would you like to integrate with app.py? (y/n): ").lower().strip()
        
        if response in ['y', 'yes']:
            success = integrate_agentic_ai()
            if success:
                create_database_tables()
                print_access_instructions()
                
                print("\\n🎉 INTEGRATION COMPLETE!")
                print("\\nNext steps:")
                print("1. Run the SQL script to create database tables")
                print("2. Restart your Flask application")
                print("3. Visit http://localhost:5000/agentic_ai")
            else:
                print("\\n❌ Integration failed. Check the error messages above.")
        else:
            print("\\n📝 Manual Integration Instructions:")
            print_access_instructions()
    else:
        print("\\n❌ Some agentic AI files are missing.")
        print("Please ensure all required files are created first.")
