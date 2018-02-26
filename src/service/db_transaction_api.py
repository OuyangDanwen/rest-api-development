import datetime
import mongoengine
import schema
from app import bcrypt

# Note that password salting is taken care of by the bycrypt library
# TODO: proper exception handling
def registerUser(username, fullname, password):
    con = mongoengine.connect('diary_app', host = 'localhost', port = 27017)
    user = schema.User(
        username = username, 
        fullname = fullname,
        password = bcrypt.generate_password_hash(password),
        createdOn = datetime.datetime.now(), 
        lastLogin = datetime.datetime.now(),
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