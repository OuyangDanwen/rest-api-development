import json
import unittest
import pymongo
from pymongo import MongoClient
from bson import ObjectId
import mongoengine

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.app.testing = True
        self.app = app.app.test_client()
        pass

    def tearDown(self):
        pass

    def test_index(self):
        index = self.app.get('/')
        response = json.loads(index.get_data())
        assert response['status']

    def test_db_setup(self):
        client = MongoClient('localhost', 27017)
        #test initial state of the database
        self.assertTrue('local' in client.database_names())
        self.assertTrue('test_db' not in client.database_names())
        #test insertion of an entry
        db = client.test_db
        collection = db.test_collection
        entry = {'text' : 'test'}
        _id = collection.insert_one(entry).inserted_id
        self.assertEqual(collection.find_one({'_id': ObjectId(_id)})['text'], 'test')
        #test creation of the test database
        self.assertTrue('test_db' in client.database_names())
        #test removal of the entry
        collection.remove({'_id': ObjectId(_id)})
        self.assertIsNone(collection.find_one({'_id': ObjectId(_id)}))
        #test removal of the test database
        db.test_collection.drop()
        client.drop_database('test_db')
        self.assertTrue('test_db' not in client.database_names())
        client.close()   

    def test_db_register_user(self):
        db_transaction_api.registerUser('testuser', 'testuser', 'test', 20)
        result = schema.User.objects(username = 'testuser', fullname = 'testuser', age = 20)
        # one exact match should be found
        self.assertEqual(len(result), 1)
        schema.User.objects(username = 'testuser', fullname = 'testuser', age = 20).delete()
        result = schema.User.objects(username = 'testuser', fullname = 'testuser', age = 20)
        # no match should be found
        self.assertFalse(result)

    def test_db_insert_post(self):
        db_transaction_api.registerUser('testuser', 'testuser', 'test', 20)
        user = schema.User.objects(username = 'testuser', fullname = 'testuser', age = 20)[0]
        db_transaction_api.insertPost(user, "test", True, "this is a test post")
        result = schema.Post.objects(author = user, isPublic = True, 
            title = "test", text = "this is a test post")
        # one exact match should be found
        self.assertEqual(len(result), 1)
        schema.Post.objects(author = user, isPublic = True, 
            title = "test", text = "this is a test post").delete()
        result = schema.Post.objects(author = user, isPublic = True, 
            title = "test", text = "this is a test post")
        # no match should be found
        self.assertFalse(result)
        schema.User.objects(username = 'testuser', fullname = 'testuser', age = 20).delete()

if __package__ is None:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from service import app, db_transaction_api, schema
else:
    from ..service import app, db_transaction_api, schema

if __name__ == '__main__':
    unittest.main()
