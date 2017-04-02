import os
from unittest import TestCase
from warnings import catch_warnings

from gateway.exceptions import UploadTargetPathAlreadyExists
from .request_mock import RequestMock


class RequestTestCase(TestCase):

    def test_request_method(self):
        request = RequestMock()
        request.method = 'POST'
        self.assertEqual(request.method, 'POST')

    def test_url(self):
        request = RequestMock()
        request.scheme = 'https'
        request.host = 'myserver.com:8080'
        request.path = '/dashboard/products'
        request.query_string = 'page=1&order=price'
        self.assertEqual(request.url, 'https://myserver.com:8080/dashboard/products?page=1&order=price')

    def test_scheme(self):
        request = RequestMock()
        request.scheme = 'https'
        self.assertEqual(request.scheme, 'https')

    def test_host(self):
        request = RequestMock()
        request.host = 'myserver.com:8080'
        self.assertEqual(request.host, 'myserver.com:8080')

    def test_path(self):
        request = RequestMock()
        request.path = '/dashboard/products'
        self.assertEqual(request.path, '/dashboard/products')

    def test_query_string(self):
        request = RequestMock()
        request.query_string = 'page=1&order=price'
        self.assertEqual(request.query_string, 'page=1&order=price')

    def test_body(self):
        request = RequestMock()
        request.body = b'<h1>Hello World</h1>'
        self.assertEqual(request.body, b'<h1>Hello World</h1>')

    def test_query(self):
        request = RequestMock()
        request.query_string = 'page=1&order=price'
        self.assertEqual(request.query, {'page': '1', 'order': 'price'})

    def test_ip(self):
        request = RequestMock()
        request.ip = '127.0.0.1'
        self.assertEqual(request.ip, '127.0.0.1')

    def test_ip_with_x_forwarded_for_header(self):
        request = RequestMock()
        request.env['HTTP_X_FORWARDED_FOR'] = '203.0.113.195, 70.41.3.18, 150.172.238.178'
        self.assertEqual(request.ip, '203.0.113.195')

    def test_form(self):
        request = RequestMock()
        request.method = 'POST'
        request.body = b'page=1&order=price'
        self.assertEqual(request.form, {'page': '1', 'order': 'price'})

    def test_reapeated_form_keys_should_appear_as_list(self):
        request = RequestMock()
        request.method = 'POST'
        request.body = b'name=john&name=doe'
        self.assertEqual(request.form, {'name': ['john', 'doe']})

    def test_files(self):
        request = RequestMock()
        request.method = 'POST'
        request.env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        request.env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            request.body = f.read()
        self.assertEqual(request.form, {'name': 'john', 'age': '23'})
        self.assertIn('photo', request.files)
        self.assertEqual(request.files['photo'].name, 'photo.png')
        self.assertEqual(request.files['photo'].type, 'image/png')

    def test_reapeated_file_keys_should_appear_as_list(self):
        request = RequestMock()
        request.method = 'POST'
        request.env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryBVTLBY0oBUmCLVZ2'
        request.env['CONTENT_LENGTH'] = '2117'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-name-photo-photo'), 'rb') as f:
            request.body = f.read()
        self.assertEqual(request.form, {'name': ['john', 'doe']})
        self.assertEqual(len(request.files['photo']), 2)
        self.assertEqual(request.files['photo'][1].name, 'photo2.png')

    def test_save_file(self):
        request = RequestMock()
        request.method = 'POST'
        request.env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        request.env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            request.body = f.read()
        photo = request.files['photo']
        target = '/tmp/gateway-test-save-file'
        if os.path.exists(target):
            os.remove(target)
        photo.save(target)
        self.assertTrue(os.path.exists(target))
        self.assertGreater(os.stat(target).st_size, 0)
        with self.assertRaises(UploadTargetPathAlreadyExists):
            photo.save(target)
        os.remove(target)

    def test_trying_to_save_file_to_existent_target_raises_exception(self):
        request = RequestMock()
        request.method = 'POST'
        request.env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        request.env['CONTENT_LENGTH'] = '1173'
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'multipart-form-data', 'name-age-photo'), 'rb') as f:
            request.body = f.read()
        photo = request.files['photo']
        target = '/tmp/gateway-test-save-file'
        with open(target, 'wb') as f:
            f.write(b'hello world')
        with self.assertRaises(UploadTargetPathAlreadyExists):
            photo.save(target)
        os.remove(target)

    def test_accessing_files_while_none_is_sent_issues_warning_about_enctype(self):
        request = RequestMock()
        request.method = 'POST'
        request.body = b'name=john&name=doe'
        with catch_warnings(record=True) as w:
            request.files
            self.assertEqual(len(w), 1)
