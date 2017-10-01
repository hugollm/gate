from unittest import TestCase
from gatekeeper import JsonResponse


class JsonResponseTestCase(TestCase):

    def test_defaults(self):
        response = JsonResponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers, {'Content-Type': 'application/json; charset=utf-8'})
        self.assertEqual(response.body, b'null')
