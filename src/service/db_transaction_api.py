from datetime import datetime
import mongoengine
import uuid

import schema

# Only use this class with `with` as in `with Db(...) as db`
class Db:
    def __init__(self, app, db='diary', host='localhost', port=27017):
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
        user = schema.User(
            createdOn = datetime.now(),
            lastLogin = datetime.now(),
            **values
        )
        try:
            return user.save()
        except mongoengine.NotUniqueError:
            return False
        except mongoengine.ValidationError:
            return None

    # Returns a token on success or None on failure
    def generateToken(self, username, password, **kw):
        token = None
        users = schema.User.objects(username=username)
        user = users and users[0] or None
        if user and self.app.bcrypt.check_password_hash(user.password, password):
            token = uuid.uuid4()
            session = schema.Session(
                user = user,
                token = token
            ).save()
        return token

    # Returns a User list of length 1 or empty list on failure
    def validateToken(self, token):
        try:
            sessions = schema.Session.objects(token = token)
            if sessions:
                return sessions[0].user
        except ValueError:
            pass
        return None

    # Returns true on success or false otherwise
    def deleteToken(self, token):
        try:
            return schema.Session.objects(token = token).delete() > 0
        except ValueError:
            return False

    # Note that author should be a User object as the reference key
    def insertPost(self, token, title, isPublic, text):
        user = self.validateToken(token) if isinstance(token, basestring) else token
        if user:
            postID = schema.Counter.objects()[0].value
            post = schema.Post(
                _id = postID,
                author = user,
                title = title,
                isPublic = isPublic,
                text = text,
                publishDate = datetime.now()
            )
            try:
                post.save()
                schema.Counter.objects().update(value = postID + 1)
                return postID
            except mongoengine.ValidationError:
                return None

    # Returns true on success or false on failure
    def deletePost(self, token, postID):
        user = self.validateToken(token)
        return user and schema.Post.objects(author = user, _id = postID).delete() > 1

    # Returns true on success or false on failure
    def adjustPostPermission(self, token, postID, isPublic):
        user = self.validateToken(token)
        return user and schema.Post.objects(author = user, _id = postID) \
            .update(isPublic = not isPublic)

    # Returns a list of posts of an authenticated user on success or false on failure
    def retrieveAllPosts(self, token):
        user = self.validateToken(token)
        if user:
            return schema.Post.objects(user = user)
        return False

    # Returns a list of all public posts
    def retrieveAllPosts(self):
        return schema.Post.objects(isPublic = True)
