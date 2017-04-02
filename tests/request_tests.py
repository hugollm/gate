from unittest import TestCase
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
