# Investor Terminal Export Module

Self-contained minimal package to integrate the Investor Terminal analytics into a new Flask project.

## Contents
- `models.py` – Minimal data models (`InvestorAccount`, `InvestorPortfolioStock`, etc.)
- `auth.py` – Session-based `api_login_required` decorator
- `blueprint.py` – Flask blueprint exposing `/api/investor_terminal/*` endpoints (simulated analytics)
- `templates/investor_terminal.html` – Lightweight reference template
- `static/css/investor_terminal.css` – Styles for the reference template
- `static/js/investor_terminal.js` – Frontend fetch logic

## Quick Integration
```python
# app.py (new project)
from flask import Flask, render_template, session
from investor_terminal_export.blueprint import bp as investor_bp
from investor_terminal_export.models import db, InvestorAccount

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'change-me'

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(investor_bp)

@app.route('/terminal')
def investor_terminal_page():
    # Ensure login simulation
    if 'investor_id' not in session:
        acct = InvestorAccount.query.first()
        if not acct:
            acct = InvestorAccount(id='demo1', name='Demo User', email='demo@example.com', password_hash='x')
            db.session.add(acct); db.session.commit()
        session['investor_id'] = acct.id
    return render_template('investor_terminal.html')

if __name__ == '__main__':
    app.run(debug=True)
```

## Endpoints
See `blueprint.py`. All require session `investor_id`.

## Replace Simulations
Swap random values with real data providers gradually (risk metrics, market data, options chain, economic calendar).

## License
Internal use. Add appropriate license if distributing.
