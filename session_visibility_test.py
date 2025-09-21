from app import app, db, AnalystProfile, AnalystConnectProfile, AnalystAvailability, InvestorAccount, SessionBooking
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json, random

def seed():
    with app.app_context():
        db.create_all()
        analyst = AnalystProfile.query.filter_by(email='vis_analyst@example.com').first()
        if not analyst:
            analyst = AnalystProfile(name='visanalyst', full_name='Visibility Analyst', email='vis_analyst@example.com', password_hash=generate_password_hash('pass'))
            db.session.add(analyst); db.session.commit()
        cp = AnalystConnectProfile.query.filter_by(analyst_id=analyst.id).first()
        if not cp:
            cp = AnalystConnectProfile(analyst_id=analyst.id, is_enabled=True, auto_confirm=True, headline='Vis Test')
            db.session.add(cp)
        dow = datetime.utcnow().weekday()
        avail = AnalystAvailability.query.filter_by(analyst_id=analyst.id, weekday=dow).first()
        if not avail:
            avail = AnalystAvailability(analyst_id=analyst.id, weekday=dow, start_minute=9*60, end_minute=12*60, slot_minutes=30)
            db.session.add(avail)
        investor = InvestorAccount.query.filter_by(email='vis_investor@example.com').first()
        if not investor:
            iid = f"INV{random.randint(0,999999):06d}"
            investor = InvestorAccount(id=iid, name='Vis Investor', email='vis_investor@example.com', password_hash=generate_password_hash('pass'), is_active=True, pan_verified=True, admin_approved=True)
            db.session.add(investor)
        db.session.commit()
        return analyst.id, investor.id

def simulate_booking(analyst_id, investor_id):
    client = app.test_client()
    # investor session for booking
    with client.session_transaction() as sess:
        sess['investor_id'] = investor_id
        sess['user_role'] = 'investor'
    start_dt = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(hours=2)
    payload = {'analyst_id': analyst_id, 'start_utc': start_dt.isoformat(), 'duration_minutes': 30}
    r = client.post('/api/analyst_sessions/book', data=json.dumps(payload), content_type='application/json')
    return r.get_json(), client

def fetch_as_analyst(analyst_id):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['analyst_id'] = analyst_id
        sess['user_role'] = 'analyst'
    r = client.get('/api/analyst_sessions/incoming')
    return r.get_json()

if __name__ == '__main__':
    aid, iid = seed()
    book_resp, _ = simulate_booking(aid, iid)
    analyst_view = fetch_as_analyst(aid)
    print(json.dumps({'booking_response': book_resp, 'analyst_view': analyst_view}, indent=2))
