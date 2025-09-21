from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance for the whole application
# Import 'db' from this module everywhere (app.py, blueprints, models)

db = SQLAlchemy()
