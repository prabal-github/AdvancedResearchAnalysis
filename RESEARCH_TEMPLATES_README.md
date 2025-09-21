# Research Templates & AI Simulation Features

This document describes the new Research Templates and AI Simulation features added to the Research Quality App.

## 🆕 New Features Overview

### 1. Research Templates with Predefined Structures
- **Event Details**: Macro triggers, timeframes, and catalysts
- **Direct Impact Metrics**: EPS changes, margin sensitivity, revenue exposure
- **Cross-Asset Correlations**: Sector and asset correlation analysis
- **Analyst Confidence Scores**: Probability weightings and severity tiers

### 2. AI Simulation Engine
- Advanced scenario analysis powered by AI
- Simulate market impacts (inflation, interest rates, currency, etc.)
- Detailed explanations and quantitative results
- Knowledge base integration for improved accuracy

## 🚀 Getting Started

### Installation & Setup

1. **Run Database Migration**
   ```bash
   python migrate_template_features.py
   ```
   This creates the required database tables and default templates.

2. **Start the Application**
   ```bash
   python app.py
   ```

3. **Test the Features**
   ```bash
   python test_template_features.py
   ```

### Accessing New Features

1. **Research Templates**
   - Navigate to: `Reports` → `Research Templates`
   - Or visit: `http://localhost:5008/research_templates`

2. **AI Simulation Engine**
   - Navigate to: `AI Tools` → `AI Simulation Engine`
   - Or visit: `http://localhost:5008/ai_simulation`

## 📋 Research Templates

### Available Template Types

1. **Inflation Impact Analysis**
   - Analyze inflation effects on stocks and sectors
   - Pre-defined triggers: RBI policy, commodity prices
   - Impact metrics: EPS sensitivity, margin contraction

2. **Interest Rate Impact Analysis**
   - Assess rate hike/cut impacts on financial markets
   - Focus on banking, NBFC, and rate-sensitive sectors
   - NIM expansion/contraction analysis

3. **Sector Shock Analysis**
   - Evaluate sector-specific disruptions
   - Regulatory changes, technology disruption
   - Competitive threat assessment

4. **Currency Impact Analysis**
   - USD/INR movement effects on businesses
   - Export/import revenue exposure analysis
   - IT and Pharma sector focus

### Using Research Templates

1. **Browse Templates**: View all available templates with descriptions
2. **Select Template**: Choose appropriate template for your analysis
3. **Fill Structure**: Complete predefined sections:
   - Event details (triggers, timeframe, catalysts)
   - Impact metrics (EPS, margins, revenue)
   - Correlations (sector, cross-asset)
   - Confidence scores (probabilities, severity)
4. **Generate Report**: Create structured analysis report

### Template Structure Example

```json
{
  "event_details": {
    "macro_triggers": ["Inflation rate changes", "RBI policy decisions"],
    "timeframe": "Q3 2025",
    "catalysts": ["RBI rate hikes", "Supply chain disruptions"]
  },
  "impact_metrics": {
    "eps_change": "-5% if inflation >5%",
    "margin_sensitivity": "Every 1% inflation → 0.7% operating margin contraction",
    "revenue_exposure": "70% revenue USD-denominated → benefits from INR depreciation"
  },
  "correlations": {
    "sector_correlation": "IT sector stocks drop 2x faster than Nifty50 during inflation shocks",
    "asset_correlation": "TCS.NS vs USD/INR correlation: -0.8"
  },
  "confidence": {
    "probability_weighting": "80% likelihood of high inflation scenario",
    "severity_tiers": "Moderate inflation: 4-5%, Severe: >6%"
  }
}
```

## 🤖 AI Simulation Engine

### Simulation Capabilities

1. **Scenario Analysis**
   - Inflation impact simulations
   - Interest rate change effects
   - Currency fluctuation impacts
   - Sector shock assessments

2. **Quantitative Results**
   - EPS impact estimates
   - Price movement predictions
   - Margin sensitivity analysis
   - Confidence scoring

3. **Learning System**
   - Saves query patterns for future use
   - Improves accuracy over time
   - Knowledge base integration

### Using AI Simulation

1. **Ask Natural Language Questions**
   ```
   "What happens to TCS.NS if inflation increases by 10%?"
   "How would a 50 basis point rate hike affect banking stocks?"
   "If USD/INR moves to 85, what is the impact on IT sector?"
   ```

2. **Get Detailed Analysis**
   - Quantitative impact estimates
   - Transmission mechanisms explained
   - Secondary effects identified
   - Risk factors highlighted
   - Timeline expectations

3. **Review Results**
   - Confidence level indicators
   - Related research reports
   - Knowledge gaps identified
   - Historical pattern references

### Example Simulation Query

**Query**: "If inflation increases by 10%, what will be the impact on TCS.NS?"

**AI Response**:
- **EPS Impact**: -7.2% (based on margin compression and cost pressures)
- **Price Impact**: -4.8% (considering defensive USD revenue exposure)
- **Margin Impact**: -1.2% (operational leverage effects)
- **Confidence**: 78% (high data availability for IT sector inflation analysis)

**Detailed Analysis**: The AI explains transmission mechanisms, compares with historical patterns, and identifies key risk factors.

## 🗄️ Database Schema

### New Tables Added

1. **research_template**: Stores predefined report templates
2. **template_report**: Reports created using templates
3. **simulation_query**: AI simulation queries and results
4. **simulation_knowledge_base**: Learning data for simulations

### Key Relationships

- Templates → Template Reports (1:many)
- Simulation Queries → Knowledge Base (1:many)
- Knowledge Base → Report Analysis (integration)

## 🎯 Use Cases

### For Analysts
1. **Structured Analysis**: Use templates for consistent, comprehensive research
2. **Scenario Testing**: Simulate various market conditions
3. **Impact Quantification**: Get specific impact estimates
4. **Quality Improvement**: Follow best-practice structures

### For Investors
1. **What-if Analysis**: Test investment scenarios
2. **Risk Assessment**: Understand potential impacts
3. **Decision Support**: Data-driven investment decisions
4. **Market Understanding**: Learn transmission mechanisms

### For Administrators
1. **Template Management**: Create and modify analysis templates
2. **Knowledge Curation**: Review and enhance simulation accuracy
3. **Performance Monitoring**: Track analysis quality improvements
4. **System Learning**: Monitor AI learning progress

## 🔧 Configuration

### Environment Variables
```bash
# No additional environment variables required
# Uses existing Flask app configuration
```

### Database Configuration
- Uses existing SQLite database
- New tables created automatically during migration
- No additional database setup required

## 📊 Monitoring & Analytics

### Template Usage Analytics
- Track most popular templates
- Monitor completion rates
- Analyze quality improvements

### Simulation Performance
- Query response times
- Accuracy feedback
- Learning curve metrics
- Knowledge gap identification

## 🚦 API Endpoints

### Research Templates
- `GET /research_templates` - List all templates
- `GET /template/{id}` - View specific template
- `POST /create_template_report/{id}` - Create report from template
- `GET /template_report/{id}` - View template report

### AI Simulation
- `GET /ai_simulation` - Simulation interface
- `POST /api/run_simulation` - Execute simulation
- `GET /api/simulation_history` - User's simulation history
- `GET /simulation/{id}` - View simulation result

### Administrative
- `POST /api/create_default_templates` - Initialize templates

## 🐛 Troubleshooting

### Common Issues

1. **Templates Not Loading**
   - Run migration script: `python migrate_template_features.py`
   - Check database permissions
   - Verify table creation

2. **AI Simulation Errors**
   - Check LLM integration (Ollama/OpenAI)
   - Verify network connectivity
   - Review error logs

3. **Navigation Links Missing**
   - Clear browser cache
   - Check template updates
   - Restart Flask application

### Debug Commands
```bash
# Test feature accessibility
python test_template_features.py

# Check database tables
python -c "from app import app, db; app.app_context().push(); print(db.engine.table_names())"

# Verify templates exist
python -c "from app import app, ResearchTemplate; app.app_context().push(); print(ResearchTemplate.query.count())"
```

## 📈 Future Enhancements

### Planned Features
1. **Custom Templates**: User-created template types
2. **Advanced Simulations**: Multi-factor scenario analysis
3. **Visualization**: Interactive charts for simulation results
4. **Collaboration**: Shared templates and simulations
5. **API Integration**: External data source connections
6. **Mobile Support**: Responsive design improvements

### Enhancement Requests
- Submit feature requests via GitHub issues
- Contribute templates via pull requests
- Share simulation patterns for learning

## 📞 Support

### Getting Help
1. Check this documentation first
2. Run the test script to identify issues
3. Review error logs in the console
4. Check existing GitHub issues

### Contributing
1. Fork the repository
2. Create feature branches
3. Submit pull requests
4. Follow coding standards

---

**Note**: These features integrate seamlessly with existing functionality and maintain backward compatibility. No existing features are modified or removed.
