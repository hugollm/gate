from unittest import TestCase
from gatekeeper import HtmlResponse


class HtmlResponseTestCase(TestCase):

    def test_defaults(self):
        response = HtmlResponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers, {'Content-Type': 'text/html; charset=utf-8'})
        self.assertEqual(response.body, b'')

    def test_set_message_sets_a_cookie_with_a_prefix(self):
        response = HtmlResponse()
        response.set_message('success', 'Operation completed')
        expected_cookie = 'MESSAGE:success="Operation completed"'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_unset_message_unsets_a_cookie_with_a_prefix(self):
        response = HtmlResponse()
        response.unset_message('success')
        expected_cookie = 'MESSAGE:success=; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())
