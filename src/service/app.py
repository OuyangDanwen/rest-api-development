#!/usr/bin/python

from flask import Flask, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import json
import os

from db_transaction_api import Db
import schema

app = Flask(__name__)
# Enable cross origin sharing for all endpoints
CORS(app)
bcrypt = Bcrypt(app)

# Get the endpoint list from all the @app.route calls
ENDPOINT_LIST = []
def new_app_route_decorator(endpoint, **kwargs):
    global ENDPOINT_LIST
    ENDPOINT_LIST.append(endpoint)
    return default_app_route_decorator(endpoint, **kwargs)
default_app_route_decorator, app.route = app.route, new_app_route_decorator

def make_json_response(data, status=True, resource={}, code=200):
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
    with open("./team_members.txt") as f:
        team_members = f.read().strip().split("\n")
    return make_json_response(team_members)

@app.route("/users", methods=['POST'])
def users():
    """Retrieve user information"""
    with Db() as db:
        token = request.get_json()['token']
        if not token:
            return make_json_response('Invalid authentication token.', False)
        user = {"username": "testuser", "fullname": "testname", "age": 0}
        return make_json_response(None, True, user)

@app.route("/users/register", methods=['POST'])
def users_register():
    """Register a user"""
    user = request.get_json()
    if user["username"] == "testuser":
        return make_json_response("User already exists!", False)
    return make_json_response(None)

@app.route("/users/authenticate", methods=['POST'])
def users_authenticate():
    """Authenticate a user"""
    body = request.get_json()
    if not body["username"]:
        return make_json_response(None, False)
    return make_json_response(None, True, {"token": "6bf00d02-dffc-4849-a635-a21b08500d61"})

@app.route("/users/expire", methods=['POST'])
def users_expire():
    """Expire an authentication token"""
    token = request.get_json()['token']
    return make_json_response(None, not token)

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
    app.run(debug=False, port=8080, host="0.0.0.0")
