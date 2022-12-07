from flask import Flask
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)

    from .statistics import statistics
    app.register_blueprint(statistics, url_prefix='/')

    return app
