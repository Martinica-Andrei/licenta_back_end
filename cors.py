from flask_cors import CORS

def init_cors(app):
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})