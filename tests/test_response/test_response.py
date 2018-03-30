import os.path
from datetime import datetime
from http.cookies import CookieError
from tempfile import NamedTemporaryFile
from types import GeneratorType

from unittest import TestCase
from unittest.mock import Mock

from gatekeeper import Response
from gatekeeper.template_renderer import TemplateRenderer
from gatekeeper.exceptions import TemplateRendererNotSet


class ResponseTestCase(TestCase):

    def assert_response(self, response, expected_status=None, expected_headers=None, expected_body=None):
        start_response = Mock()
        body = response.wsgi(start_response)
        status = start_response.call_args[0][0]
        headers = start_response.call_args[0][1]
        if expected_status is not None:
            self.assertEqual(status, expected_status)
        if expected_headers is not None:
            expected_headers = sorted(expected_headers.items())
            headers = sorted(headers)
            self.assertEqual(headers, expected_headers)
        if expected_body is not None:
            self.assertEqual(body, (expected_body,))

    def test_default_values(self):
        response = Response()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(response.body, b'')

    def test_string_gets_converted_to_bytes_when_set_to_body(self):
        response = Response()
        response.body = 'hello world'
        self.assertEqual(response.body, b'hello world')

    def test_can_concatenate_bytes_to_previously_set_body_string(self):
        response = Response()
        response.body = 'hello'
        response.body += b' world'
        self.assertEqual(response.body, b'hello world')

    def test_setting_body_converts_any_object_into_its_string_representation(self):
        response = Response()
        response.body = {'foo': 'bar'}
        self.assertEqual(response.body, b"{'foo': 'bar'}")

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
        expected_status = '400 Bad Request'
        expected_headers = {'Content-Type': 'application/json', 'Content-Length': '26'}
        expected_body = b'{"error": "Invalid token"}'
        self.assert_response(response, expected_status, expected_headers, expected_body)

    def test_string_body_gets_converted_to_bytes(self):
        response = Response()
        response.body = 'hello world'
        self.assertEqual(response._wsgi_body(), (b'hello world',))

    def test_content_length_header_is_set_for_the_response(self):
        response = Response()
        response.body = 'hello world'
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': '11'}
        expected_body = b'hello world'
        self.assert_response(response, expected_status, expected_headers, expected_body)

    def test_content_length_header_is_correct_even_with_special_characters_in_body(self):
        response = Response()
        response.body = 'blasé'
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': '6'}
        expected_body = 'blasé'.encode('utf-8')
        self.assert_response(response, expected_status, expected_headers, expected_body)

    def test_header_keys_are_case_insensitive(self):
        response = Response()
        response.headers['foo'] = 'bar'
        self.assertEqual(response.headers['FOO'], 'bar')

    def test_file_gets_returned_as_generator_to_wsgi(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'hello world')
            tmpfile.seek(0)
            response.file(tmpfile.name)
            start_respose = Mock()
            self.assertIsInstance(response.wsgi(start_respose), GeneratorType)

    def test_all_file_contents_are_yielded_by_its_generator(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'hello world')
            tmpfile.seek(0)
            response.file(tmpfile.name)
            start_respose = Mock()
            file_generator = response.wsgi(start_respose)
            contents = b''
            for chunk in file_generator:
                contents += chunk
            self.assertEqual(contents, b'hello world')

    def test_setting_file_with_specified_mime_type(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            response.file(tmpfile.name, type='image/png')
            self.assertEqual(response.headers['Content-Type'], 'image/png')

    def test_setting_file_without_specified_mime_type_makes_it_guess(self):
        response = Response()
        with NamedTemporaryFile(suffix='.png') as tmpfile:
            response.file(tmpfile.name)
            self.assertEqual(response.headers['Content-Type'], 'image/png')

    def test_setting_file_without_extension_changes_content_type_to_octet_stream(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            response.file(tmpfile.name)
            self.assertEqual(response.headers['Content-Type'], 'application/octet-stream')

    def test_setting_file_for_download(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            response.file(tmpfile.name, download=True)
            filename = os.path.basename(tmpfile.name)
            self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename="{}"'.format(filename))

    def test_setting_file_with_name(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            response.file(tmpfile.name, name='image.png')
            self.assertEqual(response.headers['Content-Disposition'], 'inline; filename="image.png"')

    def test_setting_file_without_name_puts_the_path_filename_in_the_header(self):
        response = Response()
        with NamedTemporaryFile(suffix='.png') as tmpfile:
            response.file(tmpfile.name)
            filename = os.path.basename(tmpfile.name)
            self.assertEqual(response.headers['Content-Disposition'], 'inline; filename="{}"'.format(filename))

    def test_setting_file_for_download_with_name(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            response.file(tmpfile.name, download=True, name='image.png')
            self.assertEqual(response.headers['Content-Disposition'], 'attachment; filename="image.png"')

    def test_setting_file_for_download_includes_a_content_length_header(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'foobar')
            tmpfile.seek(0)
            response.file(tmpfile.name, download=True, name='image.png')
            self.assertEqual(response.headers['Content-Length'], '6')

    def test_setting_inexistent_file_for_download_triggers_exception(self):
        response = Response()
        with self.assertRaises(FileNotFoundError):
            response.file('foobar.file')

    def test_file_method_returns_the_response(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            returned_value = response.file(tmpfile.name)
        self.assertEqual(returned_value, response)

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

    def test_render_works_when_template_renderer_is_set(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_response/templates')
        response = Response()
        response.template_renderer = renderer
        response.render('simple.html')
        self.assertEqual(response.body, b'<h1>Simple</h1>')

    def test_render_fails_if_template_renderer_is_not_set(self):
        response = Response()
        with self.assertRaises(TemplateRendererNotSet):
            response.render('simple.html')

    def test_render_can_provide_a_context_to_template(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_response/templates')
        response = Response()
        response.template_renderer = renderer
        response.render('with_context.html', {'name': 'John'})
        self.assertEqual(response.body, b'<h1>Hello John</h1>')

    def test_render_method_returns_response(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_response/templates')
        response = Response()
        response.template_renderer = renderer
        self.assertEqual(response.render('simple.html'), response)
