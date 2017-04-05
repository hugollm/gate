from unittest import TestCase
from gatekeeper.responses.html_response import HtmlResponse


class HtmlResponseTestCase(TestCase):

    def test_defaults(self):
        response = HtmlResponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers, {'Content-Type': 'text/html; charset=utf-8'})
        self.assertEqual(response.body, b'')
