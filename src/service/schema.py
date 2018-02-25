from mongoengine import *
import datetime

class User(Document):
    username = StringField(required = True, unique = True)
    email = EmailField(required = True, unique = True)
    password = StringField(required = True)
    createdOn = DateTimeField(required = True)
    lastLogin = DateTimeField(default = datetime.datetime.now())
    meta = {'alias' : "dairy_app"}