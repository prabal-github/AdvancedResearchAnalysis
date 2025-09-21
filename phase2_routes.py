#!/usr/bin/env python3
"""
Phase 2 Enhanced Features Routes
This file contains Flask routes demonstrating Phase 2 enhancements:
- HTMX for dynamic content loading
- ApexCharts for modern charts
- Select2 for better form controls
- AOS for scroll animations
"""

from flask import Blueprint, render_template, request, jsonify, flash
import random
import json
from datetime import datetime, timedelta

# Create blueprint for Phase 2 routes
phase2_bp = Blueprint('phase2', __name__)

@phase2_bp.route('/phase2/dashboard')
def enhanced_dashboard():
    """Main Phase 2 enhanced dashboard"""
    return render_template('phase2_enhanced_dashboard.html')

@phase2_bp.route('/api/enhanced-submit', methods=['POST'])
def enhanced_submit():
    """Handle enhanced form submission with HTMX"""
    try:
        stocks = request.form.getlist('stocks')
        analysis_type = request.form.get('analysis_type')
        time_period = request.form.get('time_period', '3')
        
        # Simulate processing
        result_html = f"""
        <div class="alert alert-success animate__animated animate__fadeInUp">
            <h6 class="alert-heading">Analysis Complete!</h6>
            <p class="mb-1"><strong>Stocks:</strong> {', '.join(stocks) if stocks else 'None selected'}</p>
            <p class="mb-1"><strong>Type:</strong> {analysis_type}</p>
            <p class="mb-0"><strong>Period:</strong> {time_period} months</p>
        </div>
        
        <div class="mt-3">
            <h6>Quick Insights:</h6>
            <ul class="list-unstyled">
                <li><i class="bi bi-check-circle text-success me-2"></i>Portfolio risk: Moderate</li>
                <li><i class="bi bi-check-circle text-success me-2"></i>Expected return: 8.5%</li>
                <li><i class="bi bi-check-circle text-success me-2"></i>Correlation: 0.72</li>
            </ul>
            <button class="btn btn-sm btn-enhanced" onclick="showSuccessNotification('Detailed report generated!')">
                <i class="bi bi-download me-1"></i>Download Report
            </button>
        </div>
        """
        
        return result_html
    
    except Exception as e:
        return f"""
        <div class="alert alert-danger animate__animated animate__shakeX">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Error processing analysis: {str(e)}
        </div>
        """

@phase2_bp.route('/api/sample-data/<data_type>')
def sample_data(data_type):
    """Provide sample data for HTMX dynamic loading"""
    
    if data_type == 'performance':
        return """
        <div class="animate__animated animate__fadeInUp">
            <h6 class="text-primary mb-3">
                <i class="bi bi-graph-up me-2"></i>Performance Overview
            </h6>
            <div class="row">
                <div class="col-6">
                    <div class="text-center">
                        <div class="h4 text-success mb-0">+12.3%</div>
                        <small class="text-muted">This Quarter</small>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center">
                        <div class="h4 text-primary mb-0">+24.8%</div>
                        <small class="text-muted">This Year</small>
                    </div>
                </div>
            </div>
            <div class="progress mt-3" style="height: 8px;">
                <div class="progress-bar" role="progressbar" style="width: 75%; background: var(--success-gradient);" aria-valuenow="75" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <small class="text-muted">vs S&P 500 Benchmark</small>
        </div>
        """
    
    elif data_type == 'portfolio':
        return """
        <div class="animate__animated animate__fadeInUp">
            <h6 class="text-primary mb-3">
                <i class="bi bi-briefcase me-2"></i>Portfolio Summary
            </h6>
            <div class="list-group list-group-flush">
                <div class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <div>
                        <div class="fw-semibold">Apple Inc.</div>
                        <small class="text-muted">AAPL</small>
                    </div>
                    <div class="text-end">
                        <div class="fw-semibold text-success">+2.4%</div>
                        <small class="text-muted">$15,420</small>
                    </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <div>
                        <div class="fw-semibold">Microsoft Corp.</div>
                        <small class="text-muted">MSFT</small>
                    </div>
                    <div class="text-end">
                        <div class="fw-semibold text-success">+1.8%</div>
                        <small class="text-muted">$12,350</small>
                    </div>
                </div>
                <div class="list-group-item d-flex justify-content-between align-items-center px-0">
                    <div>
                        <div class="fw-semibold">Tesla Inc.</div>
                        <small class="text-muted">TSLA</small>
                    </div>
                    <div class="text-end">
                        <div class="fw-semibold text-danger">-0.9%</div>
                        <small class="text-muted">$8,970</small>
                    </div>
                </div>
            </div>
        </div>
        """
    
    elif data_type == 'alerts':
        return """
        <div class="animate__animated animate__fadeInUp">
            <h6 class="text-primary mb-3">
                <i class="bi bi-bell me-2"></i>Recent Alerts
            </h6>
            <div class="list-group list-group-flush">
                <div class="list-group-item px-0">
                    <div class="d-flex align-items-center">
                        <div class="alert-icon me-3" style="background: var(--success-gradient); border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                            <i class="bi bi-arrow-up text-white small"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-semibold">Price Target Reached</div>
                            <small class="text-muted">AAPL reached your target of $185</small>
                        </div>
                        <small class="text-muted">2h ago</small>
                    </div>
                </div>
                <div class="list-group-item px-0">
                    <div class="d-flex align-items-center">
                        <div class="alert-icon me-3" style="background: var(--warning-gradient); border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                            <i class="bi bi-exclamation text-white small"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-semibold">Risk Alert</div>
                            <small class="text-muted">Portfolio volatility increased</small>
                        </div>
                        <small class="text-muted">4h ago</small>
                    </div>
                </div>
                <div class="list-group-item px-0">
                    <div class="d-flex align-items-center">
                        <div class="alert-icon me-3" style="background: var(--info-gradient); border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;">
                            <i class="bi bi-info text-white small"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="fw-semibold">New Research</div>
                            <small class="text-muted">Analyst report available for MSFT</small>
                        </div>
                        <small class="text-muted">1d ago</small>
                    </div>
                </div>
            </div>
        </div>
        """
    
    else:
        return """
        <div class="alert alert-warning animate__animated animate__headShake">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Unknown data type requested
        </div>
        """

@phase2_bp.route('/api/holdings/table')
def holdings_table():
    """Generate sample holdings table with HTMX pagination"""
    
    # Sample holdings data
    holdings = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'shares': 150, 'price': 185.20, 'change': 2.4, 'value': 27780},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'shares': 80, 'price': 335.50, 'change': 1.8, 'value': 26840},
        {'symbol': 'GOOGL', 'name': 'Alphabet Inc.', 'shares': 45, 'price': 142.30, 'change': -0.5, 'value': 6403.50},
        {'symbol': 'AMZN', 'name': 'Amazon.com Inc.', 'shares': 120, 'price': 145.80, 'change': 3.1, 'value': 17496},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'shares': 90, 'price': 248.50, 'change': -1.2, 'value': 22365},
        {'symbol': 'META', 'name': 'Meta Platforms Inc.', 'shares': 65, 'price': 325.75, 'change': 2.8, 'value': 21173.75},
        {'symbol': 'NVDA', 'name': 'NVIDIA Corp.', 'shares': 40, 'price': 465.20, 'change': 4.2, 'value': 18608},
        {'symbol': 'NFLX', 'name': 'Netflix Inc.', 'shares': 25, 'price': 425.30, 'change': -0.8, 'value': 10632.50},
    ]
    
    table_html = """
    <div class="table-responsive">
        <table class="table table-hover mb-0">
            <thead style="background: var(--gray-100);">
                <tr>
                    <th>Symbol</th>
                    <th>Company</th>
                    <th class="text-end">Shares</th>
                    <th class="text-end">Price</th>
                    <th class="text-end">Change</th>
                    <th class="text-end">Value</th>
                    <th width="50">Actions</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, holding in enumerate(holdings):
        change_class = 'text-success' if holding['change'] >= 0 else 'text-danger'
        change_icon = 'bi-arrow-up' if holding['change'] >= 0 else 'bi-arrow-down'
        
        table_html += f"""
        <tr class="animate__animated animate__fadeInUp" style="animation-delay: {i * 0.05}s;">
            <td>
                <div class="fw-semibold">{holding['symbol']}</div>
            </td>
            <td>
                <div class="fw-medium">{holding['name']}</div>
            </td>
            <td class="text-end">{holding['shares']}</td>
            <td class="text-end">${holding['price']:.2f}</td>
            <td class="text-end {change_class}">
                <i class="bi {change_icon} me-1"></i>{holding['change']:+.1f}%
            </td>
            <td class="text-end fw-semibold">${holding['value']:,.2f}</td>
            <td>
                <div class="dropdown">
                    <button class="btn btn-sm btn-link text-muted" data-bs-toggle="dropdown">
                        <i class="bi bi-three-dots-vertical"></i>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" hx-get="/api/holdings/{holding['symbol']}/details" hx-target="#holdings-details">View Details</a></li>
                        <li><a class="dropdown-item" href="#" onclick="showInfoNotification('Trade {holding['symbol']}')">Trade</a></li>
                        <li><a class="dropdown-item" href="#" onclick="showInfoNotification('Analyze {holding['symbol']}')">Analyze</a></li>
                    </ul>
                </div>
            </td>
        </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    
    <!-- Pagination -->
    <div class="d-flex justify-content-between align-items-center p-3 border-top">
        <small class="text-muted">Showing 1-8 of 8 holdings</small>
        <nav>
            <ul class="pagination pagination-sm mb-0">
                <li class="page-item disabled">
                    <span class="page-link">Previous</span>
                </li>
                <li class="page-item active">
                    <span class="page-link">1</span>
                </li>
                <li class="page-item disabled">
                    <span class="page-link">Next</span>
                </li>
            </ul>
        </nav>
    </div>
    """
    
    return table_html

@phase2_bp.route('/api/metric/<metric_type>/details')
def metric_details(metric_type):
    """Provide detailed metric information"""
    
    details = {
        'total-return': {
            'title': 'Total Return Analysis',
            'description': 'Your portfolio has generated a total return of 24.8% over the selected period.',
            'breakdown': [
                {'label': 'Capital Gains', 'value': '$18,430', 'percentage': '74.2%'},
                {'label': 'Dividends', 'value': '$4,890', 'percentage': '19.7%'},
                {'label': 'Interest', 'value': '$1,527', 'percentage': '6.1%'}
            ]
        },
        'risk-score': {
            'title': 'Risk Score Breakdown',
            'description': 'Your portfolio risk score of 7.2 indicates moderate risk exposure.',
            'breakdown': [
                {'label': 'Market Risk', 'value': '6.8', 'percentage': '40%'},
                {'label': 'Sector Risk', 'value': '7.4', 'percentage': '35%'},
                {'label': 'Credit Risk', 'value': '7.5', 'percentage': '25%'}
            ]
        },
        'sharpe-ratio': {
            'title': 'Sharpe Ratio Analysis',
            'description': 'A Sharpe ratio of 1.85 indicates excellent risk-adjusted returns.',
            'breakdown': [
                {'label': 'Portfolio Return', 'value': '12.3%', 'percentage': '65%'},
                {'label': 'Risk-free Rate', 'value': '4.2%', 'percentage': '20%'},
                {'label': 'Portfolio Volatility', 'value': '8.1%', 'percentage': '15%'}
            ]
        },
        'volatility': {
            'title': 'Volatility Metrics',
            'description': 'Portfolio volatility of 18.5% is within acceptable risk parameters.',
            'breakdown': [
                {'label': 'Daily Volatility', 'value': '1.2%', 'percentage': '30%'},
                {'label': 'Monthly Volatility', 'value': '5.4%', 'percentage': '45%'},
                {'label': 'Annual Volatility', 'value': '18.5%', 'percentage': '25%'}
            ]
        }
    }
    
    if metric_type not in details:
        return """
        <div class="alert alert-warning">
            <i class="bi bi-exclamation-triangle me-2"></i>
            Metric details not available
        </div>
        """
    
    detail = details[metric_type]
    
    html = f"""
    <div class="card animate__animated animate__slideInUp">
        <div class="card-header" style="background: var(--info-gradient); color: white;">
            <h6 class="mb-0">{detail['title']}</h6>
        </div>
        <div class="card-body">
            <p class="text-muted mb-3">{detail['description']}</p>
            <div class="row">
    """
    
    for item in detail['breakdown']:
        html += f"""
                <div class="col-md-4 mb-2">
                    <div class="text-center p-2 border rounded">
                        <div class="fw-semibold text-primary">{item['value']}</div>
                        <small class="text-muted">{item['label']}</small>
                        <div class="progress mt-1" style="height: 4px;">
                            <div class="progress-bar" style="width: {item['percentage']}; background: var(--primary-gradient);"></div>
                        </div>
                    </div>
                </div>
        """
    
    html += """
            </div>
            <div class="text-center mt-3">
                <button class="btn btn-sm btn-enhanced" onclick="this.parentElement.parentElement.parentElement.parentElement.remove()">
                    <i class="bi bi-x-circle me-1"></i>Close Details
                </button>
            </div>
        </div>
    </div>
    """
    
    return html

def register_phase2_routes(app):
    """Register Phase 2 routes with the Flask app"""
    app.register_blueprint(phase2_bp)
    return app

if __name__ == "__main__":
    # This can be run independently for testing
    from flask import Flask
    
    app = Flask(__name__)
    app.secret_key = 'phase2-demo-key'
    
    register_phase2_routes(app)
    
    @app.route('/')
    def index():
        return '<a href="/phase2/dashboard">Go to Phase 2 Enhanced Dashboard</a>'
    
    app.run(debug=True, port=5001)
