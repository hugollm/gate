import json
from unittest import TestCase

from gate.requests.json_request import JsonRequest
from .factory import mock_env


class JsonRequestTestCase(TestCase):

    def test_json(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'{"page": 1, "order": "price"}')
        env['wsgi.input'].seek(0)
        request = JsonRequest(env)
        self.assertEqual(request.json, {'page': 1, 'order': 'price'})

    def test_invalid_json(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'')
        env['wsgi.input'].seek(0)
        request = JsonRequest(env)
        with self.assertRaises(json.decoder.JSONDecodeError):
            request.json

    def test_null(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'null')
        env['wsgi.input'].seek(0)
        request = JsonRequest(env)
        self.assertIsNone(request.json)

    def test_get_request(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'GET'
        env['wsgi.input'].write(b'{"page": 1, "order": "price"}')
        env['wsgi.input'].seek(0)
        request = JsonRequest(env)
        self.assertEqual(request.json, {'page': 1, 'order': 'price'})
