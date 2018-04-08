from datetime import datetime, date, time, timezone
from decimal import Decimal
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

    def test_decimal_values_can_be_serialized(self):
        response = JsonResponse()
        response.json['decimal'] = Decimal('3.9')
        self.assertEqual(response.body, b'{"decimal": 3.9}')

    def test_datetime_values_can_be_serialized(self):
        response = JsonResponse()
        response.json['datetime'] = datetime(2018, 4, 7, 23, 7, 42).replace(tzinfo=timezone.utc)
        self.assertEqual(response.body, b'{"datetime": "2018-04-07T23:07:42+00:00"}')

    def test_date_values_can_be_serialized(self):
        response = JsonResponse()
        response.json['date'] = date(2018, 4, 7)
        self.assertEqual(response.body, b'{"date": "2018-04-07"}')

    def test_time_values_can_be_serialized(self):
        response = JsonResponse()
        response.json['time'] = time(23, 7, 42).replace(tzinfo=timezone.utc)
        self.assertEqual(response.body, b'{"time": "23:07:42+00:00"}')
