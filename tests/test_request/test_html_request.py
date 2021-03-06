import os
from unittest import TestCase
from warnings import catch_warnings

from gatekeeper import HtmlRequest, HtmlResponse
from gatekeeper.exceptions import UploadTargetAlreadyExists, ResponseNotSet
from .factory import mock_env


class HtmlRequestTestCase(TestCase):

    def test_form(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'page=1&order=price')
        env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        self.assertEqual(request.form, {'page': '1', 'order': 'price'})

    def test_request_can_access_form_after_body(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'page=1&order=price')
        env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        request.body
        self.assertEqual(request.form, {'page': '1', 'order': 'price'})

    def test_request_can_access_body_after_form(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'page=1&order=price')
        env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        request.form
        self.assertEqual(request.body, b'page=1&order=price')

    def test_reapeated_form_keys_should_appear_as_list(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'name=john&name=doe')
        env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        self.assertEqual(request.form, {'name': ['john', 'doe']})

    def test_files(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            env['wsgi.input'].write(f.read())
            env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        self.assertEqual(request.form, {'name': 'john', 'age': '23'})
        self.assertIn('photo', request.files)
        self.assertEqual(request.files['photo'].name, 'photo.png')
        self.assertEqual(request.files['photo'].type, 'image/png')

    def test_can_access_files_after_body(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            env['wsgi.input'].write(f.read())
            env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        request.body
        self.assertIn('photo', request.files)
        self.assertEqual(request.files['photo'].name, 'photo.png')
        self.assertEqual(request.files['photo'].type, 'image/png')

    def test_reapeated_file_keys_should_appear_as_list(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryBVTLBY0oBUmCLVZ2'
        env['CONTENT_LENGTH'] = '2117'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-name-photo-photo'), 'rb') as f:
            env['wsgi.input'].write(f.read())
            env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        self.assertEqual(request.form, {'name': ['john', 'doe']})
        self.assertEqual(len(request.files['photo']), 2)
        self.assertEqual(request.files['photo'][1].name, 'photo2.png')

    def test_save_file(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            env['wsgi.input'].write(f.read())
            env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        photo = request.files['photo']
        target = '/tmp/test-save-uploaded-file'
        if os.path.exists(target):
            os.remove(target)
        photo.save(target)
        self.assertTrue(os.path.exists(target))
        self.assertGreater(os.stat(target).st_size, 0)
        with self.assertRaises(UploadTargetAlreadyExists):
            photo.save(target)
        os.remove(target)

    def test_trying_to_save_file_to_existent_target_raises_exception(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            env['wsgi.input'].write(f.read())
            env['wsgi.input'].seek(0)
        request = HtmlRequest(env)
        photo = request.files['photo']
        target = '/tmp/test-save-uploaded-file'
        with open(target, 'wb') as f:
            f.write(b'hello world')
        with self.assertRaises(UploadTargetAlreadyExists):
            photo.save(target)
        os.remove(target)

    def test_accessing_files_while_none_is_sent_issues_warning_about_enctype(self):
        env = mock_env()
        env['REQUEST_METHOD'] = 'POST'
        env['wsgi.input'].write(b'page=1&order=price')
        request = HtmlRequest(env)
        with catch_warnings(record=True) as w:
            request.files
            self.assertEqual(len(w), 1)

    def test_messages(self):
        env = mock_env()
        env['HTTP_COOKIE'] = 'MESSAGE:foo=bar; MESSAGE:bar=biz'
        request = HtmlRequest(env)
        request.response = HtmlResponse()
        self.assertEqual(request.messages, {'foo': 'bar', 'bar': 'biz'})

    def test_accessing_messages_requires_a_response_to_be_set(self):
        env = mock_env()
        request = HtmlRequest(env)
        with self.assertRaises(ResponseNotSet):
            request.messages

    def test_accessing_messages_unsets_message_cookies(self):
        env = mock_env()
        env['HTTP_COOKIE'] = 'MESSAGE:foo=bar; MESSAGE:bar=biz'
        request = HtmlRequest(env)
        response = HtmlResponse()
        request.response = response
        request.messages
        expected_cookie = 'MESSAGE:foo=; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())
        expected_cookie = 'MESSAGE:bar=; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
        self.assertIn(('Set-Cookie', expected_cookie), response._wsgi_headers())
