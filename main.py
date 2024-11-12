from app import app
from flask_session import Session
from db import db
import api
import logging

# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

if __name__ == '__main__':
    app.register_blueprint(api.api.api_blueprint)
    db.init_app(app)
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY'] = db
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'none'
    app.config['SESSION_COOKIE_PARTITIONED'] = True
    # if true, each request refreshes the expiration date of token
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    Session(app)
    app.run(debug=True, threaded=True)