from flask_cors import CORS

def init_cors(app):
    # supports_credentials to allow cookies, authentification
    # resources specify which route to allow read access
    # allow in api endpoints, read access for this localhost
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})