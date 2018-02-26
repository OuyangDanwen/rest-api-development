#!/usr/bin/python

from flask import Flask, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import json
import os

from db_transaction_api import Db
import schema, config

app = Flask(__name__)
# Enable cross origin sharing for all endpoints
CORS(app)
bcrypt = Bcrypt(app)
setattr(app, 'bcrypt', bcrypt)

# Get the endpoint list from all the @app.route calls
ENDPOINT_LIST = []
def new_app_route_decorator(endpoint, **kwargs):
    global ENDPOINT_LIST
    ENDPOINT_LIST.append(endpoint)
    return default_app_route_decorator(endpoint, **kwargs)
default_app_route_decorator, app.route = app.route, new_app_route_decorator

TEAM_MEMBERS = ["Ngo Kim Phu", "Choo Rui Bin", "Ouyang Danwen", "Chai Wai Aik Zander"]

def make_json_response(data=None, status=True, resource={}, code=200):
    """Utility function to create the JSON responses."""
    to_serialize = dict(resource)
    to_serialize['status'] = status
    if data is not None:
        to_serialize['result' if status else 'error'] = data
    response = app.response_class(
        response=json.dumps(to_serialize),
        status=code,
        mimetype='application/json'
    )
    return response


@app.route("/")
def index():
    """Returns a list of implemented endpoints."""
    return make_json_response(ENDPOINT_LIST)


@app.route("/meta/heartbeat")
def meta_heartbeat():
    """Returns true"""
    return make_json_response(None)

@app.route("/meta/members")
def meta_members():
    """Returns a list of team members"""
    return make_json_response(TEAM_MEMBERS)

@app.route("/users", methods=['POST'])
def users():
    """Retrieve user information"""
    with Db(app) as db:
        try:
            user = db.validateToken(request.get_json()['token'])
            if user:
                return make_json_response(None, True, {field: user[field] for field in ["username", "fullname", "age"]})
        except KeyError:
            pass
        return make_json_response('Invalid authentication token.', False)

@app.route("/users/register", methods=['POST'])
def users_register():
    """Register a user"""
    user = request.get_json()
    if user:
        with Db(app) as db:
            newUser = db.registerUser(**user)
            if newUser:
                return make_json_response(code=201)
            if newUser is not None:
                return make_json_response("User already exists!", False)
    return make_json_response("Wrong field(s)", False, code=400)

@app.route("/users/authenticate", methods=['POST'])
def users_authenticate():
    """Authenticate a user"""
    user = request.get_json()
    if user:
        try:
            with Db(app) as db:
                token = db.generateToken(**user)
                if token:
                    return make_json_response(None, True, {'token': str(token)})
                return make_json_response(None, False)
        except KeyError, TypeError:
            pass
    return make_json_response("Wrong field(s)", False, code=400)

@app.route("/users/expire", methods=['POST'])
def users_expire():
    """Expire an authentication token"""
    with Db(app) as db:
        try:
            tokenDeleted = db.deleteToken(request.get_json()['token'])
        except KeyError:
            tokenDeleted = False
        return make_json_response(None, tokenDeleted)

@app.route("/diary", methods=['GET', 'POST'])
def diary():
    """Retrieve list of diary entries"""
    diaries = [{"id": 0, "title": "Test title", "author": "testuser", "publish_date": "2018-02-24T22:34:15Z", "public": True, "text": "This is my very first diary entry!"}]
    return make_json_response(diaries)

@app.route("/diary/create", methods=['POST'])
def diary_create():
    """Create a new diary entry"""
    body = request.get_json()
    token = body["token"]
    del body["token"]
    if not token:
        return make_json_response("Invalid authentication token.", False)
    return make_json_response(2)

@app.route("/diary/delete", methods=['POST'])
def diary_delete():
    """Delete an existing diary entry"""
    body = request.get_json()
    token = body["token"]
    del body["token"]
    if not token:
        return make_json_response("Invalid authentication token.", False)
    return make_json_response(None)

@app.route("/diary/permission", methods=['POST'])
def diary_permission():
    """Adjust diary entry permissions"""
    body = request.get_json()
    token = body["token"]
    del body["token"]
    if not token:
        return make_json_response("Invalid authentication token.", False)
    return make_json_response(None)

if __name__ == '__main__':
    # Change the working directory to the script directory
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Run the application
    app.run(debug=config.debug, port=8080, host="0.0.0.0")
