from datetime import datetime
import mongoengine
import uuid

import schema
import config

# Only use this class with `with` as in `with Db(...) as db`
class Db:
    def __init__(self, app, host=config.db_host, port=config.db_port, db=config.db_db):
        self.dbconfig = locals()
        self.app = app
        del self.dbconfig['self'], self.dbconfig['app']

    def __enter__(self):
        self.con = mongoengine.connect(**self.dbconfig)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.close()

    # Password salted-hashing is taken care of by the bcrypt library
    def registerUser(self, **values):
        values['password'] = self.app.bcrypt.generate_password_hash(values['password'])
        user = schema.User(**values)
        try:
            return user.save()
        except schema.NotUniqueError:
            return False
        except schema.ValidationError:
            return None

    # Returns a token on success or None on failure
    def generateToken(self, **values):
        users = schema.User.objects(username=values['username'])
        user = users and users[0] or None
        if user and self.app.bcrypt.check_password_hash(user.password, values['password']):
            token = uuid.uuid4()
            session = schema.Session(user = user, token = token).save()
            return token

    # Returns the authenticated User or None on failure
    def validateToken(self, token):
        try:
            sessions = schema.Session.objects(token = token)
            if sessions:
                return sessions[0].user
        except ValueError:
            pass

    # Returns true on success or false otherwise
    def deleteToken(self, token):
        try:
            return schema.Session.objects(token = token).delete() > 0
        except ValueError:
            return False

    # Note that author should be a User object as the reference key
    def insertPost(self, token, **values):
        user = self.validateToken(token) if isinstance(token, basestring) else token
        if user:
            postID = schema.Counter.objects()[0].value
            post = schema.Post(
                _id = postID,
                author = user,
                title = values['title'],
                public = values['public'],
                text = values['text'],
                publish_date = datetime.now()
            )
            try:
                schema.Counter.objects().update(value = postID + 1)
                post.save()
                return postID
            except schema.ValidationError:
                return None

    # Returns a list of all public posts or of an authenticated user on success or false on failure
    def retrieveAllPosts(self, token):
        if token is None:
            return schema.Post.objects(public = True)
        user = self.validateToken(token)
        return user and schema.Post.objects(author = user)

    # Returns true on success or false on failure
    def deletePost(self, token, postID):
        user = self.validateToken(token)
        return user and schema.Post.objects(author = user, _id = postID).delete() > 0

    # Returns true on success or false on failure
    def adjustPostPermission(self, token, postID, public):
        user = self.validateToken(token)
        return user and schema.Post.objects(author = user, _id = postID).update(public = public) > 0
