from datetime import datetime
from http.cookies import CookieError
from tempfile import NamedTemporaryFile
from types import GeneratorType

from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.responses.response import Response


class ResponseTestCase(TestCase):

    def test_default_values(self):
        response = Response()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(response.body, b'')

    def test_redirect(self):
        response = Response()
        r = response.redirect('/login')
        self.assertEqual(r, response)
        self.assertEqual(response.status, 303)
        self.assertEqual(response.headers.get('Location'), '/login')

    def test_not_found(self):
        response = Response()
        r = response.not_found()
        self.assertEqual(r, response)
        self.assertEqual(response.status, 404)

    def test_bad_request(self):
        response = Response()
        r = response.bad_request()
        self.assertEqual(r, response)
        self.assertEqual(response.status, 400)

    def test_unauthorized(self):
        response = Response()
        r = response.unauthorized()
        self.assertEqual(r, response)
        self.assertEqual(response.status, 401)

    def test_forbidden(self):
        response = Response()
        r = response.forbidden()
        self.assertEqual(r, response)
        self.assertEqual(response.status, 403)

    def test_wsgi(self):
        response = Response()
        response.status = 400
        response.headers['Content-Type'] = 'application/json'
        response.body = b'{"error": "Invalid token"}'
        start_respose = Mock()
        body = response.wsgi(start_respose)
        start_respose.assert_called_with('400 Bad Request', list({'Content-Type': 'application/json'}.items()))
        self.assertEqual(body, (b'{"error": "Invalid token"}',))

    def test_string_body_gets_converted_to_bytes(self):
        response = Response()
        response.body = 'hello world'
        self.assertEqual(response._wsgi_body(), (b'hello world',))

    def test_file_gets_returned_as_generator_to_wsgi(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'hello world')
            tmpfile.seek(0)
            response.file = tmpfile.name
            start_respose = Mock()
            self.assertIsInstance(response.wsgi(start_respose), GeneratorType)

    def test_all_file_contents_are_yielded_by_its_generator(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'hello world')
            tmpfile.seek(0)
            response.file = tmpfile.name
            start_respose = Mock()
            file_generator = response.wsgi(start_respose)
            contents = b''
            for chunk in file_generator:
                contents += chunk
            self.assertEqual(contents, b'hello world')

    def test_response_object_can_be_raised(self):
        response = Response()
        with self.assertRaises(Response):
            raise response

    def test_set_cookie_with_default_configs(self):
        response = Response()
        response.set_cookie('token', 'abc')
        expected_cookie = 'token=abc; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_set_two_cookies(self):
        response = Response()
        response.set_cookie('token1', 'abc')
        response.set_cookie('token2', 'xyz')
        expected_cookie1 = 'token1=abc; HttpOnly; SameSite=Strict'
        expected_cookie2 = 'token2=xyz; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie1), response._wsgi_headers())
        self.assertIn(('Set-Cookie', expected_cookie2), response._wsgi_headers())

    def test_set_cookie_with_expires_date(self):
        response = Response()
        response.set_cookie('token', 'abc', expires=datetime(2017, 4, 9, 10, 35, 54))
        expected_cookie = 'token=abc; Expires=Sun, 09 Apr 2017 10:35:54 GMT; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_set_cookie_with_domain(self):
        response = Response()
        response.set_cookie('token', 'abc', domain='my.domain.com')
        expected_cookie = 'token=abc; Domain=my.domain.com; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_set_cookie_with_path(self):
        response = Response()
        response.set_cookie('token', 'abc', path='/foo')
        expected_cookie = 'token=abc; Path=/foo; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_set_secure_cookie(self):
        response = Response()
        response.set_cookie('token', 'abc', secure=True)
        expected_cookie = 'token=abc; Secure; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_set_insecure_cookie(self):
        response = Response()
        response.set_cookie('token', 'abc', http_only=False, same_site=False)
        expected_cookie = 'token=abc'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_set_cookie_with_all_attributes(self):
        response = Response()
        response.set_cookie('token', 'abc', expires=datetime(2017, 4, 9, 10, 35, 54), domain='my.domain.com', path='/foo', secure=True)
        expected_cookie = 'token=abc; Expires=Sun, 09 Apr 2017 10:35:54 GMT; Domain=my.domain.com; Path=/foo; Secure; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_special_characters_in_cookie_value_get_escaped(self):
        response = Response()
        response.set_cookie('token', 'abc/;,~áç[\'!""]')
        expected_cookie = 'token="abc/\\073\\054~\\341\\347[\'!\\"\\"]"; HttpOnly; SameSite=Strict'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_illegal_character_in_cookie_key_triggers_exception(self):
        response = Response()
        with self.assertRaises(CookieError):
            response.set_cookie('token;', 'abc')

    def test_unset_cookie(self):
        response = Response()
        response.unset_cookie('token')
        expected_cookie = 'token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())

    def test_unset_cookie_with_domain_and_path(self):
        response = Response()
        response.unset_cookie('token', domain='my.domain.com', path='/foo')
        expected_cookie = 'token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Domain=my.domain.com; Path=/foo'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())
