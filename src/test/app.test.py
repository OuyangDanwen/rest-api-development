import json
import unittest
import pymongo
from pymongo import MongoClient

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

    def test_db(self):
        client = MongoClient('localhost', 27017)
        #test initial state of the database
        self.assertEqual(client.database_names(), ['local'])
        #test insertion of an entry
        db = client.test_db
        collection = client.test_collection
        entry = {'text' : 'test'}
        _id = collection.insert_one(entry).insert_id
        self.assertEqual(collection.find_one({'_id': ObjectId(id)})['text'], 'test')
        #test creation of the test database
        self.assertEqual(client.database_names(), ['local', 'test_db'])
        #test removal of the entry
        collection.remove({'_id': ObjectId(id)})
        self.assertIsNone(collection.find_one({'_id': ObjectId(id)}))
        #test removal of the test database
        db.test_collection.drop()
        client.drop_database('test_db')
        self.assertEqual(client.database_names(), ['local'])

if __name__ == '__main__':
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from service import app
    else:
        from ..service import app

    unittest.main()

