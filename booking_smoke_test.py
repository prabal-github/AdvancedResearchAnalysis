from app import app, db, AnalystProfile, AnalystConnectProfile, InvestorAccount, AnalystAvailability, SessionBooking
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json

"""Quick, ad-hoc smoke test for booking flow.
Run with: python booking_smoke_test.py
Outputs JSON-like dicts for each step.
NOTE: This does not perform full teardown/migrations; run on disposable/dev DB only.
"""

def ensure_seed():
    # Must run under app context
    db.create_all()
    analyst = AnalystProfile.query.filter_by(email='analyst1@example.com').first()
    if not analyst:
        analyst = AnalystProfile(name='analyst1', full_name='Analyst One', email='analyst1@example.com', password_hash=generate_password_hash('pass123'))
        db.session.add(analyst)
        db.session.commit()
    cp = AnalystConnectProfile.query.filter_by(analyst_id=analyst.id).first()
    if not cp:
        cp = AnalystConnectProfile(analyst_id=analyst.id, is_enabled=True, auto_confirm=True, headline='Test Analyst')
        db.session.add(cp)
    avail = AnalystAvailability.query.filter_by(analyst_id=analyst.id, weekday=datetime.utcnow().weekday()).first()
    if not avail:
        avail = AnalystAvailability(analyst_id=analyst.id, weekday=datetime.utcnow().weekday(), start_minute=9*60, end_minute=11*60, slot_minutes=30)
        db.session.add(avail)
    inv = InvestorAccount.query.filter_by(email='investor1@example.com').first()
    if not inv:
        inv_id = 'INV000001'
        inv = InvestorAccount(id=inv_id, name='Investor One', email='investor1@example.com', password_hash=generate_password_hash('pass123'), is_active=True, pan_verified=True, admin_approved=True)
        db.session.add(inv)
    db.session.commit()
    return analyst, cp, inv


def run_flow():
    with app.app_context():
        analyst, cp, inv = ensure_seed()
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['investor_id'] = inv.id
            sess['user_role'] = 'investor'
        start_dt = datetime.utcnow().replace(microsecond=0, second=0) + timedelta(hours=1)
        payload = {
            'analyst_id': cp.analyst_id,
            'start_utc': start_dt.isoformat(),
            'duration_minutes': 30
        }
        resp = client.post('/api/analyst_sessions/book', data=json.dumps(payload), content_type='application/json')
        try:
            data = resp.get_json()
        except Exception:
            data = {'raw': resp.data.decode('utf-8', errors='ignore')}
        existing = [b.id for b in SessionBooking.query.all()]
        return {
            'status_code': resp.status_code,
            'response': data,
            'existing_bookings': existing
        }

if __name__ == '__main__':
    out = run_flow()
    print(json.dumps(out, indent=2, default=str))
