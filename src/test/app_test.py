import json
import unittest

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

if __package__ is None:
    import sys
    from os import path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    from service import app
else:
    from ..service import app

if __name__ == '__main__':
    unittest.main()

