from mongoengine import *
import datetime

# TODO: modification required later
class User(Document):
    username = StringField(required = True, unique = True)
    email = EmailField(required = True, unique = True)
    password = StringField(required = True)
    createdOn = DateTimeField(required = True)
    lastLogin = DateTimeField(required = True)
    