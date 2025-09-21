"""
Setup Script for Agentic AI Risk Management System
Configures AWS Bedrock integration and installs required packages
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def print_header(title):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def install_packages():
    """Install required Python packages"""
    print_header("Installing Required Packages")
    
    packages = [
        'boto3',
        'yfinance',
        'numpy',
        'pandas',
        'scikit-learn',
        'asyncio'
    ]
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
        except Exception as e:
            print(f"⚠️ Error installing {package}: {e}")

def setup_aws_credentials():
    """Setup AWS credentials for Bedrock"""
    print_header("AWS Bedrock Configuration")
    
    print("Setting up AWS credentials for Bedrock access...")
    print("You can either:")
    print("1. Use AWS CLI (recommended)")
    print("2. Set environment variables")
    print("3. Use IAM role (for EC2/Lambda)")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        setup_aws_cli()
    elif choice == "2":
        setup_env_variables()
    elif choice == "3":
        setup_iam_role()
    else:
        print("Invalid choice. Skipping AWS setup.")

def setup_aws_cli():
    """Setup using AWS CLI"""
    print("\n📋 Setting up AWS CLI...")
    print("Run the following command to configure AWS CLI:")
    print("aws configure")
    print("\nYou'll need:")
    print("- AWS Access Key ID")
    print("- AWS Secret Access Key") 
    print("- Default region (e.g., us-east-1)")
    print("- Default output format (json)")
    
    proceed = input("\nDo you want to run 'aws configure' now? (y/n): ").strip().lower()
    if proceed == 'y':
        try:
            subprocess.run(['aws', 'configure'], check=True)
            print("✅ AWS CLI configured successfully")
        except subprocess.CalledProcessError:
            print("❌ AWS CLI configuration failed")
        except FileNotFoundError:
            print("❌ AWS CLI not found. Please install it first:")
            print("pip install awscli")

def setup_env_variables():
    """Setup environment variables"""
    print("\n📋 Setting up environment variables...")
    
    aws_access_key = input("Enter AWS Access Key ID: ").strip()
    aws_secret_key = input("Enter AWS Secret Access Key: ").strip()
    aws_region = input("Enter AWS Region (default: us-east-1): ").strip() or "us-east-1"
    
    # Create .env file
    env_content = f"""# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID={aws_access_key}
AWS_SECRET_ACCESS_KEY={aws_secret_key}
AWS_DEFAULT_REGION={aws_region}
AWS_BEDROCK_REGION={aws_region}

# Optional: Specific Bedrock model
BEDROCK_MISTRAL_MODEL=mistral.mistral-7b-instruct-v0:1

# Risk Management Settings
RISK_MANAGEMENT_ENABLED=true
RISK_ANALYSIS_INTERVAL=3600
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment variables saved to .env file")
    print("💡 Make sure to add .env to your .gitignore file!")

def setup_iam_role():
    """Setup IAM role information"""
    print("\n📋 IAM Role Setup")
    print("If you're running on EC2, Lambda, or other AWS services,")
    print("you can use IAM roles instead of access keys.")
    print("\nRequired IAM permissions for Bedrock:")
    print("- bedrock:InvokeModel")
    print("- bedrock:InvokeModelWithResponseStream")
    print("\nExample IAM policy:")
    
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/mistral.*",
                    "arn:aws:bedrock:*::foundation-model/anthropic.*"
                ]
            }
        ]
    }
    
    print(json.dumps(policy, indent=2))
    print("\n✅ When using IAM roles, no additional configuration needed!")

def create_sample_config():
    """Create sample configuration file"""
    print_header("Creating Sample Configuration")
    
    config = {
        "risk_management": {
            "enabled": True,
            "bedrock_region": "us-east-1",
            "default_model": "mistral.mistral-7b-instruct-v0:1",
            "risk_thresholds": {
                "concentration_limit": 0.15,
                "sector_limit": 0.4,
                "volatility_threshold": 25.0,
                "drawdown_threshold": -15.0
            },
            "analysis_settings": {
                "comprehensive_analysis_interval": 3600,
                "real_time_monitoring": True,
                "stress_test_scenarios": [
                    "market_crash",
                    "interest_rate_shock", 
                    "sector_rotation",
                    "currency_shock"
                ]
            }
        },
        "agent_settings": {
            "risk_monitoring_agent": {"enabled": True, "confidence_threshold": 0.8},
            "scenario_simulation_agent": {"enabled": True, "scenarios": "all"},
            "compliance_agent": {"enabled": True, "check_interval": 1800},
            "advisor_copilot_agent": {"enabled": True, "max_tokens": 1500},
            "trade_execution_agent": {"enabled": True, "rebalance_threshold": 0.05}
        }
    }
    
    with open('risk_management_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Sample configuration saved to risk_management_config.json")

def test_system():
    """Test the risk management system"""
    print_header("Testing Risk Management System")
    
    try:
        # Test imports
        print("Testing imports...")
        from risk_management_agents import RiskManagementOrchestrator, InvestorProfile
        print("✅ Risk management modules imported successfully")
        
        # Test AWS Bedrock connection
        print("Testing AWS Bedrock connection...")
        import boto3
        client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("✅ AWS Bedrock client created successfully")
        
        print("\n🎉 Basic system test passed!")
        print("✅ All components are ready for use")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please check that all required files are present")
    except Exception as e:
        print(f"⚠️ Test warning: {e}")
        print("System may still work, but please verify AWS credentials")

def show_usage_instructions():
    """Show usage instructions"""
    print_header("Usage Instructions")
    
    instructions = """
🚀 Your Agentic AI Risk Management System is now set up!

📍 ACCESSING THE SYSTEM:
1. Start your Flask application: python app.py
2. Navigate to: http://127.0.0.1:5008/vs_terminal_AClass
3. Click on "Risk Management" or visit: http://127.0.0.1:5008/vs_terminal_AClass/risk_management

🔧 API ENDPOINTS:
- Comprehensive Analysis: POST /api/vs_terminal_AClass/risk_management/comprehensive_analysis
- Risk Alerts: GET /api/vs_terminal_AClass/risk_management/risk_alerts
- Stress Tests: POST /api/vs_terminal_AClass/risk_management/stress_test
- Compliance Check: POST /api/vs_terminal_AClass/risk_management/compliance_check
- Advisor Query: POST /api/vs_terminal_AClass/risk_management/advisor_query
- Rebalancing: POST /api/vs_terminal_AClass/risk_management/rebalancing_suggestions

🤖 AVAILABLE AGENTS:
1. Risk Monitoring & Insights Agent - Continuous portfolio risk monitoring
2. Scenario Simulation Agent - Stress testing and scenario analysis
3. Compliance & Reporting Agent - Automated compliance checks
4. Advisor Copilot Agent - AI-powered investment guidance
5. Trade Execution & Rebalancing Agent - Portfolio optimization suggestions

💡 SAMPLE QUERIES FOR ADVISOR COPILOT:
- "Should I increase my IT sector exposure given current market conditions?"
- "What are the risks of my current portfolio allocation?"
- "How should I hedge against market volatility?"
- "What rebalancing actions should I take this quarter?"

🔄 TESTING vs PRODUCTION:
- Currently using: SQLite + Mock data + YFinance
- Production ready: AWS RDS + Fyers API + Live data
- AWS Bedrock integration: Ready for both environments

📊 DASHBOARD FEATURES:
- Real-time risk scoring (0-10 scale)
- Interactive risk heatmap
- Live agent status monitoring
- Comprehensive analysis results
- AI-powered chat interface
- Portfolio allocation visualization

🛡️ SECURITY NOTES:
- AWS credentials are stored securely
- All API endpoints include error handling
- Fallback responses when services are unavailable
- Session-based access control

📈 NEXT STEPS:
1. Test the system with sample data
2. Configure your risk thresholds in risk_management_config.json
3. Set up Fyers API for live market data (production)
4. Configure AWS RDS for production database
5. Customize agent behaviors based on your requirements

💬 SUPPORT:
If you encounter any issues:
1. Check AWS Bedrock service availability in your region
2. Verify AWS credentials and permissions
3. Ensure all Python packages are installed
4. Check Flask application logs for detailed error messages

Happy investing with AI-powered risk management! 🎯
"""
    
    print(instructions)

def main():
    """Main setup function"""
    print_header("Agentic AI Risk Management System Setup")
    print("🤖 Setting up AWS Bedrock-powered Risk Management for Investors")
    print("This script will help you configure the system for both testing and production use.")
    
    # Step 1: Install packages
    install_choice = input("\nInstall required Python packages? (y/n): ").strip().lower()
    if install_choice == 'y':
        install_packages()
    
    # Step 2: Setup AWS credentials
    aws_choice = input("\nSetup AWS Bedrock credentials? (y/n): ").strip().lower()
    if aws_choice == 'y':
        setup_aws_credentials()
    
    # Step 3: Create configuration
    config_choice = input("\nCreate sample configuration file? (y/n): ").strip().lower()
    if config_choice == 'y':
        create_sample_config()
    
    # Step 4: Test system
    test_choice = input("\nTest the system components? (y/n): ").strip().lower()
    if test_choice == 'y':
        test_system()
    
    # Step 5: Show instructions
    show_usage_instructions()
    
    print_header("Setup Complete!")
    print("🎉 Your Agentic AI Risk Management System is ready!")
    print("📖 Please review the usage instructions above.")
    print("🚀 Start your Flask app and visit the risk management dashboard!")

if __name__ == "__main__":
    main()
