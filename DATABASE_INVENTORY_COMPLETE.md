# Complete Database Inventory for Investment Dashboard Application

## Overview
This document provides a comprehensive inventory of all databases used in the Flask investment dashboard application.

## Database Configuration
- **Primary Database Engine**: Flask-SQLAlchemy with support for both SQLite and PostgreSQL
- **Configuration File**: config.py
- **Environment Variables**: 
  - RDS_DATABASE_URL (PostgreSQL)
  - DATABASE_URL (fallback)
  - SQLite fallback: 'sqlite:///instance/investment_research.db'

## Main Application Database Models (app.py)
The main Flask application defines the following SQLAlchemy models:

### Core Models
1. **Report** - Research reports with analysis results
2. **PlagiarismMatch** - Plagiarism detection between reports
3. **SkillLearningAnalysis** - Skill learning breakdowns
4. **User** - User management
5. **Topic** - Research topics and assignments
6. **SkillCompletion** - Individual skill completions tracking
7. **AnalystSkillSummary** - Analyst skill summaries
8. **CodeArtifact** - Code artifacts and repositories
9. **CodeArtifactVersion** - Versioning for code artifacts
10. **CodeArtifactPermission** - Access control for code artifacts
11. **CodeArtifactStar** - Star/favorite system for code
12. **CodeRunRequest** - Code execution requests
13. **CodeArtifactActivity** - Activity tracking for code artifacts
14. **CertificateRequest** - Certificate generation requests
15. **CertificateTemplate** - Certificate templates
16. **PortfolioCommentary** - Portfolio analysis commentary
17. **InvestorImportedPortfolio** - Imported portfolio data
18. **InvestorImportedPortfolioHolding** - Holdings in imported portfolios
19. **RealTimePortfolio** - Real-time portfolio tracking
20. **RealTimeHolding** - Real-time holdings data
21. **FyersWebSocketSubscription** - Fyers API WebSocket subscriptions
22. **MarketDataCache** - Market data caching
23. **ContactForm** - Contact form configurations
24. **ContactFormSubmission** - Contact form submissions
25. **InvestorTradingAPIConnection** - Trading API connections
26. **SupportTicket** - Support ticket system
27. **SupportTicketHistory** - Support ticket history
28. **AnalystConnectProfile** - Analyst profiles for connections
29. **AnalystAvailability** - Analyst availability scheduling
30. **AnalystTimeOff** - Analyst time-off management
31. **SessionBooking** - Session booking system

## Investor Terminal Models (investor_terminal_export/models.py)
1. **InvestorAccount** - Investor account management
2. **InvestorPortfolioStock** - Portfolio stock holdings
3. **ChatHistory** - Chat history storage
4. **PortfolioAnalysisLimit** - Portfolio analysis rate limiting

## Agentic AI Models (agentic_models.py)
1. **InvestmentAgent** - AI agent configurations
2. **AgentAction** - Agent actions and decisions
3. **AgentRecommendation** - Agent recommendations
4. **AgentLearning** - Agent learning data
5. **AgentAlert** - Agent-generated alerts
6. **AgentPerformanceMetrics** - Agent performance tracking
7. **AgentPortfolioTracking** - Portfolio tracking by agents

## Physical Database Files

### Root Directory Databases
1. **investment_research.db**
   - Tables: portfolio_commentary, script_executions, admin_ai_settings, ai_analysis_reports, ml_execution_runs

2. **investor_accounts.db**
   - Status: Empty database

3. **investor_scripts.db**
   - Status: Empty database

4. **ml_ai_system.db** (Recently Created)
   - Tables: users, ai_agents, ml_models, portfolios, portfolio_holdings, user_subscriptions, agent_executions, model_predictions, market_data, risk_analytics, performance_analytics, system_config, notifications, chat_history

5. **ml_dashboard.db**
   - Tables: model_performance_metrics, published_model_run_history

6. **predictram_dashboard.db**
   - Status: Empty database

7. **risk_management.db**
   - Tables: risk_alerts, risk_analysis_results

8. **test.db**
   - Tables: test_table, test_unique, test_check

### Instance Directory Databases
9. **instance/google_meetings.db**
   - Tables: analyst_profiles, investor_accounts, analyst_connect_profiles, analyst_availability, session_bookings, google_calendar_tokens

10. **instance/investment_research.db** (Main Application Database)
    - 100+ tables including all main application models
    - Primary database for the Flask application
    - Contains: reports, users, portfolios, analytics, AI agents, ML models, investor data, and all application features

11. **instance/reports.db**
    - Similar structure to main database but focused on reporting
    - Tables: reports, portfolios, analytics, AI agents, and core functionality

12. **instance/research_reports.db**
    - Tables: skill_completions, analyst_skill_summary

## Database Usage Patterns

### Primary Application Database
- **Main Database**: instance/investment_research.db
- **Purpose**: Core application functionality, user management, reports, portfolios, AI/ML features
- **Models**: All SQLAlchemy models defined in app.py and related files

### Specialized Databases
- **ML/AI System**: ml_ai_system.db - Dedicated AI/ML functionality
- **Risk Management**: risk_management.db - Risk analysis and alerts
- **Google Meetings**: instance/google_meetings.db - Calendar and meeting management
- **ML Dashboard**: ml_dashboard.db - ML model performance tracking

### Development/Testing Databases
- **Test Database**: test.db - Testing purposes
- **Empty Databases**: investor_accounts.db, investor_scripts.db, predictram_dashboard.db

## Database Relationships
- Most databases are independent but some share similar schemas
- The main application database (instance/investment_research.db) contains the complete schema
- Specialized databases contain subsets of functionality for specific features
- Migration support through Flask-Migrate for schema changes

## Database Management
- **ORM**: SQLAlchemy with Flask-SQLAlchemy extension
- **Migrations**: Flask-Migrate for database schema management
- **Configuration**: Environment-based configuration in config.py
- **Connection Management**: Centralized through Flask application factory pattern

## Recent Updates
- Created ml_ai_system.db with comprehensive AI/ML catalog (12 AI agents, 10 ML models)
- Fixed syntax errors in main application (app.py line 7671)
- Database schema supports both SQLite (development) and PostgreSQL (production)

## Access Patterns
- **Primary Access**: Through Flask-SQLAlchemy ORM
- **Direct Access**: SQLite3 for database analysis and maintenance
- **API Access**: RESTful APIs for external integrations
- **Admin Access**: Administrative interfaces for database management

## Security Considerations
- Database access controlled through application authentication
- API key management for external services
- Role-based access control for different user types (admin, analyst, investor)
- Encrypted connections for production PostgreSQL databases
