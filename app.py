from flask import Flask
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, CSRFError

app = Flask(__name__)

#MODIFY LATER
app.secret_key = "test"
CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:3000"]}})

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return {"csrf" : "CSRF token is missing!"}, 400

csrf = CSRFProtect(app)
csrf.init_app(app)

