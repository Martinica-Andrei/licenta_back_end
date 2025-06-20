from most_common_words import MostCommonWords # import MostCommonWords so it can be loaded by joblib
from app import app
import api
from cors import init_cors
from db import db
from services.nearest_neighbors_service import NearestNeighborsService
from session import init_session
from csrf import csrf
from login_manager import login_manager
import logging

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

if __name__ == '__main__':
    app.register_blueprint(api.api.api_blueprint)
    init_cors(app)
    db.init_app(app)
    init_session(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    NearestNeighborsService(None).refit_neighbors()
    app.run(debug=True, threaded=True)