from flask import Flask, request, jsonify, Response
from configuration import Configuration
from flask_jwt_extended import JWTManager

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000)
