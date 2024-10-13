from app import app
from db import db
import api

if __name__ == '__main__':
    app.register_blueprint(api.blueprint.api_blueprint)
    db.init_app(app)
    app.run(debug=True)
