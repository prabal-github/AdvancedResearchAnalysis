from flask import Blueprint

options_chain_dashboard = Blueprint('options_chain_dashboard', __name__)

from .routes import options_chain_routes  # Import the routes for the options chain dashboard

# Register the routes with the blueprint
options_chain_dashboard.register_blueprint(options_chain_routes)