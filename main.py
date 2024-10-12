from app import app
import api

if __name__ == '__main__':
    app.register_blueprint(api.blueprint.api_blueprint)
    app.run(debug=True)
