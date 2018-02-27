from mongoengine import *
import uuid
import datetime

class User(Document):
    username = StringField(required = True, unique = True)
    fullname = StringField(required = True)
    password = StringField(required = True)
    age = IntField(required = True)

class Post(Document):
    _id = IntField(required = True, primary_key = True)
    title = StringField(required = True)
    author = ReferenceField(User, reverse_delete_rule=CASCADE)
    publish_date = DateTimeField(required = True)
    public = BooleanField(required = True)
    text = StringField(required = True)

class Session(Document):
    token = UUIDField(required = True, unique = True, default = uuid.uuid4)
    user = ReferenceField(User, reverse_delete_rule=CASCADE)

class Counter(Document):
    value = IntField(required = True)
