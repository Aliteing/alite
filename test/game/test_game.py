import unittest
import mongomock
from tornado.testing import AsyncTestCase, gen_test
from tornado.web import Application
from tornado.httpserver import HTTPRequest
from unittest.mock import Mock


class TestSomeHandler(AsyncTestCase):

    @gen_test
    def test_no_from_date_param(self):
        mock_application = Mock(spec=Application)
        payload_request = HTTPRequest(
            method='GET', uri='/test', headers=None, body=None
        )
        handler = SomeHandler(mock_application, payload_request)
        with self.assertRaises(ValueError):
            yield handler.get()


def increase_votes(collection):
    collection.update_many({}, {'$inc': {'votes': 1}})


class MyTestCase(unittest.TestCase):
    def test_list_mongo(self):
        # collection = mongomock.MongoClient()
        dbs = mongomock.MongoClient(host="0.0.0.0", username="username", password="passwd").list_database_names()
        print("dbs", dbs)
        self.assertEqual(dbs, [])  # add assertion here

    def test_increase_votes(self):
        collection = mongomock.MongoClient().db.collection
        objects = [dict(votes=1), dict(votes=2)]
        for obj in objects:
            obj['_id'] = collection.insert_one(obj).inserted_id
        increase_votes(collection)
        for obj in objects:
            stored_obj = collection.find_one({'_id': obj['_id']})
            stored_obj['votes'] -= 1
            # assert stored_obj == obj  # by comparing all fields we make sure only votes changed
            self.assertEqual(stored_obj, obj)  # add assertion here


if __name__ == '__main__':
    unittest.main()
