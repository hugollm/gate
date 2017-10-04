import json

from unittest import TestCase
from unittest.mock import Mock

from gatekeeper import JsonResponse


class JsonResponseTestCase(TestCase):

    def assert_json(self, json1, json2):
        dict1 = json.loads(json1.decode('utf-8'))
        dict2 = json.loads(json2.decode('utf-8'))
        self.assertEqual(dict1, dict2)

    def test_defaults(self):
        response = JsonResponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers, {'Content-Type': 'application/json; charset=utf-8'})
        self.assert_json(response.body, b'{}')

    def test_body_reflects_json_dict(self):
        response = JsonResponse()
        response.json['hello'] = 'world'
        self.assert_json(response.body, b'{"hello": "world"}')

    def test_body_freezes_after_wsgi_call(self):
        response = JsonResponse()
        response.json['hello'] = 'world'
        self.assert_json(response.body, b'{"hello": "world"}')
        response.wsgi(Mock())
        response.json['foo'] = 'bar'
        self.assert_json(response.body, b'{"hello": "world"}')

    def test_body_does_not_freeze_before_wsgi_call(self):
        response = JsonResponse()
        response.json['hello'] = 'world'
        self.assert_json(response.body, b'{"hello": "world"}')
        response.json['foo'] = 'bar'
        self.assert_json(response.body, b'{"hello": "world", "foo": "bar"}')
