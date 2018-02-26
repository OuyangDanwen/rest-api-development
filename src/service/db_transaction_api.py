import datetime
import mongoengine
import schema
import uuid
from app import bcrypt

# Note that password salting is taken care of by the bycrypt library
# TODO: proper exception handling
def registerUser(username, fullname, password, age):
    con = mongoengine.connect('diary_app', host = 'localhost', port = 27017)
    user = schema.User(
        username = username, 
        fullname = fullname,
        password = bcrypt.generate_password_hash(password),
        createdOn = datetime.datetime.now(), 
        lastLogin = datetime.datetime.now(),
        age = age
        )
    try:
        user.save()
    except NotUniqueError:
        print("Duplicates detected!")
    except ValidationError:
        print("Invalid fields!")
    con.close()

# Note that author should be a User object as the reference key
def insertPost(author, title, isPublic, text):
    con = mongoengine.connect('diary_app', host = 'localhost', port = 27017)
    post = schema.Post(
        author = author,
        title = title,
        isPublic = isPublic,
        text = text,
        publishDate = datetime.datetime.now()
        )
    try:
        post.save()
    except ValidationError:
        print("Invalid fields")
    con.close()

# Returns a token on success or None on failure
def generateToken(user, password):
    con = mongoengine.connect('diary_app', host = 'localhost', port = 27017)
    token = None
    if bycrypt.chech_password_hash(user.password, password):
        token = uuid.uuid4()
        session = schema.Session(
        user = user,
        token = token
        )
        session.save()
    con.close()
    return token

# Returns a User list of length 1 or empty list on failure
def validateToken(token):
    con = mongoengine.connect('diary_app', host = 'localhost', port = 27017)
    user = schema.User.objects(token = token)
    con.close()
    return user

# Returns true on success or false otherwise
def deleteToken(token):
    con = mongoengine.connect('diary_app', host = 'localhost', port = 27017)
    result = not not schema.session.objects(token = token).delete() 
    con.close()
    return result
