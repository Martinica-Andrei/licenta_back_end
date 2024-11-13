from flask_wtf.csrf import CSRFProtect, CSRFError
from app import app

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return {"csrf" : "CSRF token is missing!"}, 400

csrf = CSRFProtect(app)

