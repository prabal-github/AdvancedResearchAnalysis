import os
from app import app, socketio  # noqa

# This file exposes `application` for WSGI servers (gunicorn / mod_wsgi).
# For pure HTTP (no WebSockets) you could use `application = app`.
# With Flask-SocketIO in production prefer an async worker class:
# gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 wsgi:application

application = app

if __name__ == "__main__":
    # Dev fallback run (not for production scaling)
    socketio.run(app, host="0.0.0.0", port=int(os.getenv('APP_PORT','5008')), debug=True)
