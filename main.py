from app import app
from db import db
import api
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

if __name__ == '__main__':
    app.register_blueprint(api.blueprint.api_blueprint)
    db.init_app(app)
    app.run(debug=True, threaded=True)
