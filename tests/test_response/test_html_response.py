from unittest import TestCase
from gatekeeper import HtmlResponse


class HtmlResponseTestCase(TestCase):

    def test_defaults(self):
        response = HtmlResponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers, {'Content-Type': 'text/html; charset=utf-8'})
        self.assertEqual(response.body, b'')

    def test_html_responses_have_a_context_object(self):
        response = HtmlResponse()
        self.assertEqual(response.context, {})
