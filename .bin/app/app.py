# app.py
from flask import Flask
from flask_cors import CORS
import os

def create_app(config=None):
    """Application factory"""
    
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-key')
    app.config['JSON_SORT_KEYS'] = False
    
    if config:
        app.config.update(config)
    
    CORS(app)
    
    # ========== REGISTER BLUEPRINTS ==========
    from routes.auth import auth_bp
    from routes.devices import devices_bp
    from routes.system import system_bp
    from routes.automations import automations_bp
    from routes.security import security_bp
    from routes.music import music_bp
    from routes.ai import ai_bp
    from routes.server import server_bp
    from routes.setup import setup_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(automations_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(music_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(server_bp)
    app.register_blueprint(setup_bp)
    
    if system_bp:  # Windows only
        app.register_blueprint(system_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)