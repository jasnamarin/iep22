from flask import Flask, request, Response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from configuration import Configuration
from models import database, User, UserRole, Role
from sqlalchemy import and_
from utils import role_check
import re

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route('/register', methods=['POST'])
def register():
    forename = request.json.get('forename', '')
    surname = request.json.get('surname', '')
    email = request.json.get('email', '')
    password = request.json.get('password', '')
    customer_flag = request.json.get('isCustomer', '')

    message = None
    if forename is None or len(forename) == 0:
        message = 'Field forename is missing.'
    elif surname is None or len(surname) == 0:
        message = 'Field surname is missing.'
    elif email is None or len(email) == 0:
        message = 'Field email is missing.'
    elif password is None or len(password) == 0:
        message = 'Field password is missing.'
    elif customer_flag is None or customer_flag == '':
        message = 'Field isCustomer is missing.'

    if message is not None:
        return jsonify(message=message), 400

    result = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)
    if result is None:
        message = 'Invalid email.'
    elif len(password) < 8 or re.search('[a-z]+', password) is None or re.search('[A-Z]+', password) is None or \
            re.search('[0-9]+', password) is None:
        message = 'Invalid password.'
    elif User.query.filter(User.email == email).first() is not None:
        message = 'Email already exists.'

    if message is not None:
        return jsonify(message=message), 400

    user = User(forename=forename, surname=surname, email=email, password=password)
    database.session.add(user)
    database.session.commit()

    if customer_flag is True:
        role_name = 'customer'
    else:
        role_name = 'warehouse'
    role = Role.query.filter(Role.name == role_name).first().id
    user_role = UserRole(userId=user.id, roleId=role)
    database.session.add(user_role)
    database.session.commit()

    return Response(status=200)


@application.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    message = None
    if email is None or len(email) == 0:
        message = 'Field email is missing.'
    elif password is None or len(password) == 0:
        message = 'Field password is missing.'
    else:
        result = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)
        if result is None:
            message = 'Invalid email.'

    if message is None:
        user = User.query.filter(and_(User.email == email, User.password == password)).first()
        if not user:
            message = 'Invalid credentials.'

    if message is not None:
        return jsonify(message=message), 400

    additional_claims = {
        'forename': user.forename,
        'surname': user.surname,
        'roles': [role.name for role in user.roles]
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken=access_token, refreshToken=refresh_token), 200


@application.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    if identity is None:
        return jsonify(msg='Missing Authorization Header'), 401

    additional_claims = {
        'forename': refresh_claims['forename'],
        'surname': refresh_claims['surname'],
        'roles': refresh_claims['roles']
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)

    return jsonify(accessToken=access_token), 200


@application.route('/', methods=['GET'])
def index():
    return 'Hello world!'


@application.route('/delete', methods=['POST'])
@role_check('admin')
def delete():
    message = None
    email = request.json.get('email', '')
    if email is None or len(email) == 0:
        message = 'Field email is missing.'
    else:
        result = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email)
        if result is None:
            message = 'Invalid email.'

    if message is None:
        user = User.query.filter(User.email == email).first()
        if not user:
            message = 'Unknown user.'

    if message is not None:
        return jsonify(message=message), 400

    database.session.delete(user)
    database.session.commit()

    return Response(status=200)


if __name__ == '__main__':
    database.init_app(application)
    application.run(debug=True, host='0.0.0.0', port=5002)
