"""Ad-hoc migration script for session booking feature enhancements.

Run once in a maintenance window. Steps:
1. Ensure no active app writers during run.
2. Back up DB.
3. Execute this script (python migrations_session_feature.py) with correct DATABASE_URL env (if using Postgres) or same config as app.

Actions:
- Create unique constraint uq_session_slot on session_bookings if not present.
- Create session_feedback table if not present.
- Backfill session_feedback from legacy prefixed notes.

Supports SQLite (dev) and Postgres (preferred production). MySQL would need syntax adjustments.
"""
from datetime import datetime
from app import db, SessionBooking, SessionBookingNote, SessionFeedback  # reuse models
from sqlalchemy import text
from sqlalchemy.engine import reflection

engine = db.engine
conn = engine.connect()
inspector = reflection.Inspector.from_engine(engine)

def has_constraint(table, name):
    try:
        for uc in inspector.get_unique_constraints(table):
            if uc.get('name') == name:
                return True
    except Exception:
        return False
    return False

# 1. Unique constraint
if not has_constraint('session_bookings', 'uq_session_slot'):
    dialect = engine.dialect.name
    print('Adding unique constraint uq_session_slot ...')
    if dialect == 'postgresql':
        conn.execute(text('ALTER TABLE session_bookings ADD CONSTRAINT uq_session_slot UNIQUE (analyst_id, start_utc, end_utc);'))
    else:
        # SQLite auto handled by SQLAlchemy model metadata on next create_all; attempt manual
        try:
            conn.execute(text('CREATE UNIQUE INDEX uq_session_slot ON session_bookings (analyst_id, start_utc, end_utc);'))
        except Exception as e:
            print('Index create skipped/failed:', e)
else:
    print('Constraint uq_session_slot already present.')

# 2. Create session_feedback table if missing
if 'session_feedback' not in inspector.get_table_names():
    print('Creating session_feedback table...')
    SessionFeedback.__table__.create(bind=engine)
else:
    print('session_feedback table already exists.')

# 3. Backfill
existing_fb = db.session.query(SessionFeedback.id).limit(1).first()
if existing_fb:
    print('Feedback table already populated; skipping backfill.')
else:
    print('Backfilling feedback from legacy notes...')
    legacy = SessionBookingNote.query.filter(SessionBookingNote.note.startswith('[FEEDBACK rating=')).all()
    added = 0
    for n in legacy:
        try:
            prefix = n.note.split(']')[0]
            r = int(prefix.split('rating=')[1])
            if not (1 <= r <= 5):
                continue
        except Exception:
            continue
        # find booking / investor
        b = SessionBooking.query.filter_by(id=n.booking_id).first()
        if not b:
            continue
        if SessionFeedback.query.filter_by(booking_id=b.id, investor_id=n.author_id).first():
            continue
        fb = SessionFeedback(booking_id=b.id, investor_id=n.author_id, analyst_id=b.analyst_id, rating=r, comment=n.note[len(prefix)+2:][:4000])
        db.session.add(fb)
        added += 1
        if added % 100 == 0:
            db.session.commit()
    db.session.commit()
    print(f'Backfill complete. Added {added} feedback rows.')

print('Migration script finished.')
