from app import app, db, SessionBooking
from datetime import datetime, timedelta

def set_admin_session(client):
    with client.session_transaction() as sess:
        sess['is_admin'] = True
    sess['user_role'] = 'admin'
    sess['admin_authenticated'] = True


def seed_session():
    # Ensure a sample booking exists for admin listing
    if SessionBooking.query.first() is None:
        b = SessionBooking()
        b.investor_id = 'INVTEST'
        b.analyst_id = 1
        b.start_utc = datetime.utcnow()
        b.end_utc = datetime.utcnow() + timedelta(hours=1)
        b.status = 'completed'
        db.session.add(b)
        db.session.commit()


def test_admin_sessions_endpoint():
    with app.test_client() as client:
        with app.app_context():
            seed_session()
        client.get('/admin_login')  # establish session
        set_admin_session(client)
        r = client.get('/api/admin/sessions')
        assert r.status_code == 200, r.data
        data = r.get_json()
        assert data['ok'] is True
        if data['sessions']:
            assert 'video_recording_url' in data['sessions'][0]

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    test_admin_sessions_endpoint()
    print('Endpoint test passed.')
