from mongoengine import *
import uuid
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
    _id = IntField(required = True, primary_key = True)
    title = StringField(required = True)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    publishDate = DateTimeField(required = True)
    isPublic = BooleanField(required = True)
    text = StringField(required = True)

class Session(Document):
    user = ReferenceField(User, reverse_delete_rule=CASCADE)
    token = UUIDField(required = True, unique = True, default = uuid.uuid4)

class Counter(Document):
    value = IntField(required = True)
