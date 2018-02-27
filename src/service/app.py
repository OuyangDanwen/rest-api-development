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

def make_json_response(data=None, status=True, code=200):
    """Utility function to create the JSON responses."""
    to_serialize = {'status': status}
    if data is not None:
        to_serialize['result' if status else 'error'] = data
    return app.response_class(
        response=json.dumps(to_serialize),
        status=code,
        mimetype='application/json'
    )

@app.route("/")
def index():
    """Returns a list of implemented endpoints."""
    return make_json_response(ENDPOINT_LIST)


@app.route("/meta/heartbeat")
def meta_heartbeat():
    """Returns true"""
    return make_json_response()

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
                return make_json_response({field: user[field] for field in ["username", "fullname", "age"]})
        except KeyError:
            pass
        return make_json_response('Invalid authentication token.', False)

@app.route("/users/register", methods=['POST'])
def users_register():
    """Register a user"""
    user = request.get_json()
    if user:
        with Db(app) as db:
            try:
                newUser = db.registerUser(**user)
                if newUser:
                    return make_json_response(code=201)
                if newUser is not None:
                    return make_json_response("User already exists!", False)
            except KeyError:
                pass
    return make_json_response("Wrong field(s)", False, 400)

@app.route("/users/authenticate", methods=['POST'])
def users_authenticate():
    """Authenticate a user"""
    user = request.get_json()
    if user:
        try:
            with Db(app) as db:
                token = db.generateToken(**user)
                if token:
                    return make_json_response({'token': str(token)})
                return make_json_response(None, False)
        except KeyError, TypeError:
            pass
    return make_json_response("Wrong field(s)", False, 400)

@app.route("/users/expire", methods=['POST'])
def users_expire():
    """Expire an authentication token"""
    with Db(app) as db:
        try:
            tokenDeleted = db.deleteToken(request.get_json()['token'])
        except KeyError:
            tokenDeleted = False
        return make_json_response(None, tokenDeleted)

def entryFromPost(post):
    entry = post._data # Just a cached representation of Mongo object that can be modified for convenience
    entry['id'] = entry.pop('_id')
    entry['author'] = post.author.username
    entry['publish_date'] = entry['publish_date'].isoformat()
    return entry

@app.route("/diary", methods=['GET', 'POST'])
def diary():
    """Retrieve list of diary entries"""
    with Db(app) as db:
        try:
            posts = db.retrieveAllPosts(None if request.method == 'GET' else request.get_json()['token'])
            if posts is not None:
                return make_json_response([entryFromPost(post) for post in posts])
        except KeyError:
            pass
        return make_json_response("Invalid authentication token.", False)

@app.route("/diary/create", methods=['POST'])
def diary_create():
    """Create a new diary entry"""
    try:
        body = request.get_json()
        token = body.pop('token')
        with Db(app) as db:
            try:
                postId = db.insertPost(token, **body)
                if postId is not None:
                    return make_json_response({'id': postId}, code=201)
            except KeyError:
                return make_json_response("Wrong field(s)", False, 400)
    except KeyError:
        pass
    return make_json_response("Invalid authentication token.", False)

@app.route("/diary/delete", methods=['POST'])
def diary_delete():
    """Delete an existing diary entry"""
    try:
        body = request.get_json()
        token = body.pop('token')
        with Db(app) as db:
            try:
                result = db.deletePost(token, body['id'])
                if result is not None:
                    return make_json_response(None if result else "User doesn't own this post", result)
            except KeyError:
                return make_json_response("Wrong field(s)", False, 400)
    except KeyError:
        pass
    return make_json_response("Invalid authentication token.", False)

@app.route("/diary/permission", methods=['POST'])
def diary_permission():
    """Adjust diary entry permissions"""
    try:
        body = request.get_json()
        token = body.pop('token')
        with Db(app) as db:
            try:
                result = db.adjustPostPermission(token, body['id'], body['public'])
                if result is not None:
                    return make_json_response(None if result else "User doesn't own this post", result)
            except KeyError:
                return make_json_response("Wrong field(s)", False, 400)
    except KeyError:
        pass
    return make_json_response("Invalid authentication token.", False)

if __name__ == '__main__':
    # Change the working directory to the script directory
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Run the application
    app.run(debug=config.debug, port=8080, host="0.0.0.0")
