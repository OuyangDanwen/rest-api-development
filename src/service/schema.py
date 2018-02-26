from mongoengine import *
import datetime

# TODO: modification required later
class User(Document):
    username = StringField(required = True, unique = True)
    fullname = StringField(required = True)
    password = StringField(required = True)
    createdOn = DateTimeField(required = True)
    lastLogin = DateTimeField(required = True)
    age = IntField(required = True)

class Post(Document):
	title = StringField(required = True)
	author = ReferenceField(User)
	publishDate = DateTimeField(required = True)
	isPublic = BooleanField(required = True)
	text = StringField(required = True)
