from flask import Flask, send_from_directory
from flask_cors import CORS
from . import controller
import logging

logging.basicConfig(level=logging.INFO)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.register_blueprint(controller.bp, url_prefix='/api/v1')

    cors = CORS(app, resources={r"/*": {"origins": "*"}})
    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route('/')
    def health_check():
        return 'The Planner API is running!'

    @app.route('/docs/<path:path>')
    def swagger_schema(path):
        return send_from_directory('api', path)

    return app