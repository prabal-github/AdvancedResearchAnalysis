from app import app, db, AnalystProfile, AnalystConnectProfile, AnalystAvailability, InvestorAccount, SessionBooking
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import json, sys

ANALYST_EMAIL = 'analyst@demo.com'
INVESTOR_EMAIL = 'investor@demo.com'
ANALYST_PASSWORD = 'AnalystDemo123!'
INVESTOR_PASSWORD = 'InvestorDemo123!'
INVESTOR_ID = 'INVDEMO001'

"""Seed analyst & investor and book a session.
Run: python book_demo_session.py [minutes_from_now]
Default start is +90 minutes.
"""

def ensure_entities():
    db.create_all()
    analyst = AnalystProfile.query.filter_by(email=ANALYST_EMAIL).first()
    if not analyst:
        analyst = AnalystProfile()
        analyst.name = 'analyst_demo'
        analyst.full_name = 'Demo Analyst'
        analyst.email = ANALYST_EMAIL
        analyst.password_hash = generate_password_hash(ANALYST_PASSWORD)
        analyst.is_active = True
        db.session.add(analyst)
        db.session.commit()
    cp = AnalystConnectProfile.query.filter_by(analyst_id=analyst.id).first()
    if not cp:
        cp = AnalystConnectProfile()
        cp.analyst_id = analyst.id
        cp.is_enabled = True
        cp.auto_confirm = True
        cp.headline = 'Demo Analyst'
        db.session.add(cp)
    # Ensure availability today for next few hours
    wd = datetime.utcnow().weekday()
    avail = AnalystAvailability.query.filter_by(analyst_id=analyst.id, weekday=wd).first()
    if not avail:
        avail = AnalystAvailability()
        avail.analyst_id = analyst.id
        avail.weekday = wd
        avail.start_minute = 8*60
        avail.end_minute = 18*60
        avail.slot_minutes = 30
        db.session.add(avail)
    investor = InvestorAccount.query.filter_by(email=INVESTOR_EMAIL).first()
    if not investor:
        investor = InvestorAccount()
        investor.id = INVESTOR_ID
        investor.name = 'Demo Investor'
        investor.email = INVESTOR_EMAIL
        investor.password_hash = generate_password_hash(INVESTOR_PASSWORD)
        investor.is_active = True
        investor.pan_verified = True
        investor.admin_approved = True
        db.session.add(investor)
    db.session.commit()
    return analyst, cp, investor


def create_booking(start_offset_minutes=90):
    analyst, cp, investor = ensure_entities()
    start_dt = datetime.utcnow().replace(second=0, microsecond=0) + timedelta(minutes=start_offset_minutes)
    end_dt = start_dt + timedelta(minutes=30)
    # Check if an identical booking already exists to avoid duplicate
    existing = SessionBooking.query.filter_by(analyst_id=analyst.id, start_utc=start_dt, end_utc=end_dt).first()
    if existing:
        return {'ok': True, 'message': 'Existing booking found', 'booking_id': existing.id}
    b = SessionBooking()
    b.investor_id = investor.id
    b.analyst_id = analyst.id
    b.start_utc = start_dt
    b.end_utc = end_dt
    b.status = 'confirmed'
    b.video_join_url = f"/video/session/demo-{start_dt.strftime('%H%M')}"
    b.video_host_url = b.video_join_url + '?host=1'
    db.session.add(b)
    db.session.commit()
    return {'ok': True, 'message': 'Session booked', 'booking_id': b.id, 'analyst_id': analyst.id, 'investor_id': investor.id, 'start_utc': start_dt.isoformat()}

if __name__ == '__main__':
    mins = int(sys.argv[1]) if len(sys.argv) > 1 else 90
    with app.app_context():
        out = create_booking(mins)
        print(json.dumps(out, indent=2))
