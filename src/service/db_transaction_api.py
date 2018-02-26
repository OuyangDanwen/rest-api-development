from datetime import datetime
import mongoengine
import schema
import uuid

# Only use this class with `with` as in `with Db(...) as db`
class Db:
    def __init__(self, app, db='diary', host='localhost', port=27017):
        self.app = app
        self.dbconfig = locals()
        del self.dbconfig['self'], self.dbconfig['app']

    def __enter__(self):
        self.con = mongoengine.connect(**self.dbconfig)

    def __exit__(self, exc_type, exc_value, traceback):
        self.con.close()

    # Password salted-hashing is taken care of by the bcrypt library
    # TODO: proper exception handling
    def registerUser(username, email, password):
        user = schema.User(
            username = username,
            fullname = fullname,
            password = self.app.bcrypt.generate_password_hash(password),
            createdOn = datetime.now(),
            lastLogin = datetime.now(),
            age = age
        )
        try:
            user.save()
        except NotUniqueError:
            print("Duplicates detected!")
        except ValidationError:
            print("Invalid fields!")

    # Note that author should be a User object as the reference key
    def insertPost(title, isPublic, text, token):
        user = validateTokent(token)
        if user:
            postID = schema.counter.objects()[0]
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
                schema.counter.objects().update(value = postID + 1)
                return postID
            except ValidationError:
                print("Invalid fields")
                return None

    # Returns true on success or false on failure
    def deletePost(postID, token):
        user = validateToken(token)
        return user and schema.Post.objects(author = user, _id = postID).delete() > 1

    # Returns true on success or false on failure
    def adjustPostPermission(isPublic, postID, token):
        user = validateToken(token)
        return user and schema.Post.objects(author = user, _id = postID) \
            .update(isPublic = not isPublic)

    # Returns a list of posts of an authenticated user on success or false on failure
    def retrieveAllPosts(token):
        user = validateToken(token)
        if user:
            return schema.Post.objects(user = user)
        return False

    # Returns a list of all public posts
    def retrieveAllPosts():
        return schema.Post.objects(isPublic = True)


    # Returns a token on success or None on failure
    def generateToken(user, password):
        token = None
        if self.app.bcrypt.check_password_hash(user.password, password):
            token = uuid.uuid4()
            session = schema.Session(
                user = user,
                token = token
            )
            session.save()
        return token

    # Returns a User list of length 1 or empty list on failure
    def validateToken(token):
        sessions = schema.Session.objects(token = token)
        if sessions:
            return sessions[0].user
        return None

    # Returns true on success or false otherwise
    def deleteToken(token):
        return schema.Session.objects(token = token).delete() > 0
