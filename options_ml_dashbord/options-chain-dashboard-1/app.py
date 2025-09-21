from flask import Flask
from config import Config
from routes import investor, admin
from options_chain.routes import options_chain_routes
from routes.api.options_api import options_api_routes

app = Flask(__name__)
app.config.from_object(Config)

# Register routes
app.register_blueprint(investor)
app.register_blueprint(admin)
app.register_blueprint(options_chain_routes)
app.register_blueprint(options_api_routes)

if __name__ == '__main__':
    app.run(debug=True)