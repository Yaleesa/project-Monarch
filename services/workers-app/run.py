from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_restplus import Api, Resource
from flask import current_app as app
from app.api import api
import logging



app = Flask(__name__)
api.init_app(app)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel('WARNING')
    app.run(debug=True, host='0.0.0.0')
