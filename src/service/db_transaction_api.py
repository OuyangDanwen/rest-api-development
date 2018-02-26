from datetime import datetime
import mongoengine
import schema
import uuid
from app import bcrypt

# Only use this class with `with` as in `with Db(...) as db`
class Db:
    def __init__(self, db='diary', host='localhost', port=27017):
        self.dbconfig = locals()
        del self.dbconfig['self']

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
            password = bcrypt.generate_password_hash(password),
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
    def insertPost(author, title, isPublic, text):
        post = schema.Post(
            author = author,
            title = title,
            isPublic = isPublic,
            text = text,
            publishDate = datetime.now()
        )
        try:
            post.save()
        except ValidationError:
            print("Invalid fields")

    # Returns a token on success or None on failure
    def generateToken(user, password):
        token = None
        if bycrypt.check_password_hash(user.password, password):
            token = uuid.uuid4()
            session = schema.Session(
                user = user,
                token = token
            )
            session.save()
        return token

    # Returns a User list of length 1 or empty list on failure
    def validateToken(token):
        return schema.User.objects(token = token)

    # Returns true on success or false otherwise
    def deleteToken(token):
        return schema.Session.objects(token = token).delete() > 0
