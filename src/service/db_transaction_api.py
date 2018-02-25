import datetime
from mongoengine import *
from schema import *
from flask_bcrypt import *

# Note that password salting is taken care of by the bycrypt library
def registerUser(username, email, password):
	user = User(
            username = username, 
            password = generate_password_hash(password),
            createdOn = datetime.datetime.now(), 
            email = email
        )
	user.save()


