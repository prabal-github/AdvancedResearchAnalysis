from app import app, db, AnalystProfile, AnalystConnectProfile, AnalystAvailability
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

"""Simple availability endpoint test after timezone normalization fix."""

def ensure_data():
    with app.app_context():
        db.create_all()
        analyst = AnalystProfile.query.filter_by(email='tzfix@example.com').first()
        if not analyst:
            analyst = AnalystProfile(name='tzfix', full_name='TZ Fix', email='tzfix@example.com', password_hash=generate_password_hash('x'))
            db.session.add(analyst)
            db.session.commit()
        cp = AnalystConnectProfile.query.filter_by(analyst_id=analyst.id).first()
        if not cp:
            cp = AnalystConnectProfile(analyst_id=analyst.id, is_enabled=True, auto_confirm=True, headline='TZ')
            db.session.add(cp)
        weekday = datetime.utcnow().weekday()
        avail = AnalystAvailability.query.filter_by(analyst_id=analyst.id, weekday=weekday).first()
        if not avail:
            avail = AnalystAvailability(analyst_id=analyst.id, weekday=weekday, start_minute=8*60, end_minute=9*60, slot_minutes=30)
            db.session.add(avail)
        db.session.commit()
        return analyst.id

def test_availability(aid: int):
    client = app.test_client()
    start = datetime.utcnow().isoformat()+"+00:00"
    end = (datetime.utcnow()+timedelta(days=1)).isoformat()+"+00:00"
    resp = client.get(f"/api/analysts/{aid}/availability?from={start}&to={end}")
    print('Status:', resp.status_code)
    try:
        print('JSON:', resp.get_json())
    except Exception:
        print('Raw:', resp.data[:500])

if __name__ == '__main__':
    aid = ensure_data()
    test_availability(aid)
