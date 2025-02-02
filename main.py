from most_common_words import MostCommonWords # import MostCommonWords so it can be loaded by joblib in load_user_preprocessing
from app import app
import api
from cors import init_cors
from db import db
from session import init_session
from csrf import csrf
from login_manager import login_manager
import logging
from load_book_recommendation_model import load_user_preprocessing

#logging.basicConfig()
#logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

if __name__ == '__main__':
    app.register_blueprint(api.api.api_blueprint)
    init_cors(app)
    db.init_app(app)
    init_session(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    load_user_preprocessing()
    app.run(debug=True, threaded=True)