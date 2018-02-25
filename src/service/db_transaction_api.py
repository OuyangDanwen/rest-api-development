import datetime
from flask_mongoengine import *
from schema import *
from app import bcrypt

# Note that password salting is taken care of by the bycrypt library
# TODO: proper exception handling
def registerUser(username, email, password):
	con = connect('dairy_app', host = '172.17.0.2', port =27017)
	user = User(
            username = username, 
            password = generate_password_hash(password),
            createdOn = datetime.datetime.now(), 
            email = email
        )
	try:
		user.save()
	except NotUniqueError:
		print("Duplicates detected!")
	except ValidationError:
		print("Invalid fields!")
	con.disconnect()