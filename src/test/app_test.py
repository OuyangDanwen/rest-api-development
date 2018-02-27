import unittest
import json
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import mongoengine
import uuid
from datetime import datetime

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
        def post_json(path='/', **kwargs):
            if 'json' in kwargs:
                kwargs['data'] = json.dumps(kwargs['json'])
                kwargs['content_type'] = 'application/json'
                del kwargs['json']
            return old_post(path, **kwargs)
        old_post, self.app.post = self.app.post, post_json
        self.testUsername = 'test-' + str(uuid.uuid4())

    def tearDown(self):
        with Db(app) as db:
            # This should also cascade all test diary entries and sessions
            schema.User.objects(username = {'$regex': '^' + self.testUsername}).delete()

    def test_db_setup(self):
        client = MongoClient(config.db_host, config.db_port)
        #test initial state of the database
        try:
            self.assertIn('local', client.database_names())
            self.assertNotIn('test_db', client.database_names())
            #test insertion of an entry
            db = client.test_db
            collection = db.test_collection
            entry = {'text' : 'test'}
            _id = collection.insert_one(entry).inserted_id
            self.assertEqual(collection.find_one({'_id': ObjectId(_id)})['text'], 'test')
            #test creation of the test database
            self.assertIn('test_db', client.database_names())
            #test removal of the entry
            collection.remove({'_id': ObjectId(_id)})
            self.assertIsNone(collection.find_one({'_id': ObjectId(_id)}))
            #test removal of the test database
            db.test_collection.drop()
            client.drop_database('test_db')
            self.assertNotIn('test_db', client.database_names())
        except pymongo.errors.OperationFailure as e:
            print "Skipping test_db_setup:", str(e)
        client.close()

    def test_db_register_user(self):
        testUsername = self.testUsername + '-db-user'
        with Db(app) as db:
            db.registerUser(username = testUsername, fullname = 'testuser', password = 'test', age = 20)
            result = schema.User.objects(username = testUsername, fullname = 'testuser', age = 20)
            # one exact match should be found
            self.assertEqual(len(result), 1)
            schema.User.objects(username = testUsername, fullname = 'testuser', age = 20).delete()
            result = schema.User.objects(username = testUsername, fullname = 'testuser', age = 20)
            # no match should be found
            self.assertFalse(result)

    def test_db_insert_post(self):
        testUsername = self.testUsername + '-db-post'
        with Db(app) as db:
            db.registerUser(username = testUsername, fullname = 'testuser', password = 'test', age = 20)
            user = schema.User.objects(username = testUsername, fullname = 'testuser', age = 20)[0]
            db.insertPost(user, title = testUsername, public = True, text = "this is a test post")
            result = schema.Post.objects(author = user, public = True,
                title = testUsername, text = "this is a test post")
            # one exact match should be found
            self.assertEqual(len(result), 1)
            schema.Post.objects(author = user, public = True,
                title = testUsername, text = "this is a test post").delete()
            result = schema.Post.objects(author = user, public = True,
                title = testUsername, text = "this is a test post")
            # no match should be found
            self.assertFalse(result)
            schema.User.objects(username = testUsername, fullname = 'testuser', age = 20).delete()

    def test_index(self):
        index = self.app.get('/')
        self.assertEqual(index.status_code, 200)
        response = json.loads(index.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)

    def test_meta_heartbeat(self):
        meta_heartbeat = self.app.get('/meta/heartbeat')
        self.assertEqual(meta_heartbeat.status_code, 200)
        response = json.loads(meta_heartbeat.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])

    def test_meta_members(self):
        meta_members = self.app.get('/meta/members')
        self.assertEqual(meta_members.status_code, 200)
        response = json.loads(meta_members.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)

    def test_users(self):
        testUsername = self.testUsername + '-users'
        testFullname = "Peter Test"
        testAge = 20
        body = {"username": testUsername, "password": "pass", "fullname": testFullname, "age": testAge}
        # Register new user
        users_register = self.app.post('/users/register', json=body)
        self.assertEqual(users_register.status_code, 201)
        response = json.loads(users_register.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        # Register same user
        users_register = self.app.post('/users/register', json=body)
        self.assertEqual(users_register.status_code, 200)
        response = json.loads(users_register.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])
        # Authenticate the registered user
        users_authenticate = self.app.post('/users/authenticate', json=body)
        self.assertEqual(users_authenticate.status_code, 200)
        response = json.loads(users_authenticate.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('token'))
        self.assertIsInstance(response['token'], basestring)
        token = response['token']
        body = {"token": token}
        # Retrieve authenticated user
        users = self.app.post('/users', json=body)
        self.assertEqual(users.status_code, 200)
        response = json.loads(users.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('username'))
        self.assertTrue(response.has_key('fullname'))
        self.assertTrue(response.has_key('age'))
        self.assertEqual(response['username'], testUsername)
        self.assertEqual(response['fullname'], testFullname)
        self.assertEqual(response['age'], testAge)
        # Expire authenticated token
        users_expire = self.app.post('/users/expire', json=body)
        self.assertEqual(users_expire.status_code, 200)
        response = json.loads(users_expire.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        # Assert invalidated token
        users = self.app.post('/users', json=body)
        self.assertEqual(users.status_code, 200)
        response = json.loads(users.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])

    def test_users_bogus(self):
        body = {"username": "bogus", "password": "bogus"}
        # Authenticate bogus user
        users_authenticate = self.app.post('/users/authenticate', json=body)
        self.assertEqual(users_authenticate.status_code, 200)
        response = json.loads(users_authenticate.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])
        body = {"token": "bogus"}
        # Retrieve user with bogus token
        users = self.app.post('/users', json=body)
        self.assertEqual(users.status_code, 200)
        response = json.loads(users.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])
        # Expire bogus token
        users_expire = self.app.post('/users/expire', json=body)
        self.assertEqual(users_expire.status_code, 200)
        response = json.loads(users_expire.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])

    def test_diary(self):
        testUsername = self.testUsername + '-diary'
        testUsernam2 = self.testUsername + '-diar2'
        # Register new users
        body = {"username": testUsername, "password": "pass", "fullname": "Peter Test", "age": 20}
        users_register = self.app.post('/users/register', json=body)
        self.assertEqual(users_register.status_code, 201)
        bod2 = {"username": testUsernam2, "password": "pass", "fullname": "Peter Tes2", "age": 20}
        users_register = self.app.post('/users/register', json=bod2)
        self.assertEqual(users_register.status_code, 201)
        # Authenticate the registered users
        users_authenticate = self.app.post('/users/authenticate', json=body)
        self.assertEqual(users_authenticate.status_code, 200)
        response = json.loads(users_authenticate.get_data())
        self.assertTrue(response.has_key('token'))
        token = response['token']

        users_authenticate = self.app.post('/users/authenticate', json=bod2)
        self.assertEqual(users_authenticate.status_code, 200)
        response = json.loads(users_authenticate.get_data())
        self.assertTrue(response.has_key('token'))
        toke2 = response['token']
        # Create new diary entries
        body = {"token": token, "title": testUsername, "public": True, "text": "Test"}
        diary_create = self.app.post('/diary/create', json=body)
        self.assertEqual(diary_create.status_code, 201)
        response = json.loads(diary_create.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        entryId = response['result']

        bod2 = {"token": toke2, "title": testUsernam2, "public": False, "text": "Tes2"}
        diary_create = self.app.post('/diary/create', json=bod2)
        self.assertEqual(diary_create.status_code, 201)
        response = json.loads(diary_create.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        entryI2 = response['result']
        # Retrieve all public diary entries
        diary = self.app.get('/diary')
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)
        self.assertEqual(len(response['result']), 1)

        entry = response['result'][0]
        self.assertEqual(entry["id"], entryId)
        self.assertEqual(entry["title"], testUsername)
        self.assertEqual(entry["author"], testUsername)
        self.assertIsInstance(entry["publish_date"], basestring)
        self.assertLess(entry["publish_date"], datetime.now().isoformat())
        self.assertTrue(entry["public"])
        self.assertEqual(entry["text"], "Test")
        # Retrieve all of user 2's diary entries
        diary = self.app.post('/diary', json=bod2)
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)
        self.assertEqual(len(response['result']), 1)

        entry = response['result'][0]
        self.assertEqual(entry["id"], entryI2)
        self.assertEqual(entry["title"], testUsernam2)
        self.assertEqual(entry["author"], testUsernam2)
        self.assertIsInstance(entry["publish_date"], basestring)
        self.assertLess(entry["publish_date"], datetime.now().isoformat())
        self.assertFalse(entry["public"])
        self.assertEqual(entry["text"], "Tes2")
        # Adjust users' diary permission
        bod2['id'] = entryI2
        bod2['public'] = True
        diary_permission = self.app.post('/diary/permission', json=bod2)
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])

        diary = self.app.get('/diary')
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)
        self.assertEqual(len(response['result']), 2)

        body['id'] = entryId
        body['public'] = False
        diary_permission = self.app.post('/diary/permission', json=body)
        self.assertEqual(diary_permission.status_code, 200)
        response = json.loads(diary_permission.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])

        diary = self.app.get('/diary')
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)
        self.assertEqual(len(response['result']), 1)
        # Adjust other user's diary permission
        bodyOther = {"token": token, "id": entryI2, "public": True}
        diary_permission = self.app.post('/diary/permission', json=bodyOther)
        self.assertEqual(diary_permission.status_code, 200)
        response = json.loads(diary_permission.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])
        # Delete the only public diary entry left
        diary_delete = self.app.post('/diary/delete', json=bod2)
        self.assertEqual(diary_delete.status_code, 200)
        response = json.loads(diary_delete.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])

        diary = self.app.get('/diary')
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertTrue(response['status'])
        self.assertTrue(response.has_key('result'))
        self.assertIsInstance(response['result'], list)
        self.assertEqual(len(response['result']), 0)
        # Delete other user's entry
        diary_delete = self.app.post('/diary/delete', json=bodyOther)
        self.assertEqual(diary_delete.status_code, 200)
        response = json.loads(diary_delete.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])

    def test_diary_bogus(self):
        body = {"token": "bogus", "id": -1, "title": "Bogus", "public": True, "text": "Test"}
        diary_create = self.app.post('/diary/create', json=body)
        self.assertEqual(diary_create.status_code, 200)
        response = json.loads(diary_create.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])
        self.assertFalse(response.has_key('result'))

        diary = self.app.post('/diary', json=body)
        self.assertEqual(diary.status_code, 200)
        response = json.loads(diary.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])
        self.assertFalse(response.has_key('result'))

        diary_permission = self.app.post('/diary/permission', json=body)
        self.assertEqual(diary_permission.status_code, 200)
        response = json.loads(diary_permission.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])

        diary_delete = self.app.post('/diary/delete', json=body)
        self.assertEqual(diary_delete.status_code, 200)
        response = json.loads(diary_delete.get_data())
        self.assertTrue(response.has_key('status'))
        self.assertFalse(response['status'])

if __package__ is None:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from service import app, db_transaction_api, schema, config
else:
    from ..service import app, db_transaction_api, schema, config
Db = db_transaction_api.Db

if __name__ == '__main__':
    unittest.main()
