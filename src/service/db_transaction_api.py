import datetime
import mongoengine
import schema
from app import bcrypt

# Note that password salting is taken care of by the bycrypt library
# TODO: proper exception handling
def registerUser(username, email, password):
    con = mongoengine.connect('dairy_app', host = 'localhost', port = 27017)
    user = schema.User(
            username = username, 
            password = bcrypt.generate_password_hash(password),
            createdOn = datetime.datetime.now(), 
            lastLogin = datetime.datetime.now(),
            email = email
        )
    try:
        user.save()
    except NotUniqueError:
        print("Duplicates detected!")
    except ValidationError:
        print("Invalid fields!")
    con.close()