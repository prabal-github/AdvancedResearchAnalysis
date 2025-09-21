from app import app, db, SessionBooking
from datetime import datetime
import json, sys

"""Quick CLI inspection tool for session bookings.
Usage:
  python inspect_sessions.py                # list recent 20
  python inspect_sessions.py all            # list recent 200
  python inspect_sessions.py upcoming       # upcoming 50
  python inspect_sessions.py analyst 7      # sessions for analyst 7
  python inspect_sessions.py investor INV000123  # sessions for investor
"""

limit_map={'default':20,'all':200,'upcoming':50}

mode = sys.argv[1] if len(sys.argv)>1 else 'default'
with app.app_context():
    q = SessionBooking.query
    if mode=='upcoming':
        q = q.filter(SessionBooking.start_utc >= datetime.utcnow()).order_by(SessionBooking.start_utc.asc()).limit(limit_map['upcoming'])
    elif mode=='analyst' and len(sys.argv)>2:
        aid = int(sys.argv[2])
        q = q.filter_by(analyst_id=aid).order_by(SessionBooking.start_utc.desc()).limit(200)
    elif mode=='investor' and len(sys.argv)>2:
        iid = sys.argv[2]
        q = q.filter_by(investor_id=iid).order_by(SessionBooking.start_utc.desc()).limit(200)
    else:
        lim = limit_map.get(mode, limit_map['default'])
        q = q.order_by(SessionBooking.start_utc.desc()).limit(lim)
    rows = q.all()
    print(json.dumps([{'id':r.id,'analyst_id':r.analyst_id,'investor_id':r.investor_id,'start':r.start_utc.isoformat(),'end':r.end_utc.isoformat(),'status':r.status} for r in rows], indent=2))
