from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.app import App
from gatekeeper.endpoints.endpoint import Endpoint


class AppTestCase(TestCase):

    def test_app_without_endpoints_responds_with_404(self):
        app = App()
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
        start_response = Mock()
        body = app(env, start_response)
        start_response.assert_called_once_with('404 Not Found', {'Content-Type': 'text/plain; charset=utf-8'}.items())
        self.assertEqual(body, (b'',))

    def test_app_routes_request_to_endpoint_if_it_matches(self):
        class Hello(Endpoint):
            endpoint_path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/hello'}
        start_response = Mock()
        body = app(env, start_response)
        start_response.assert_called_once_with('200 OK', {'Content-Type': 'text/plain; charset=utf-8'}.items())
        self.assertEqual(body, (b'hello world',))

    def test_app_does_not_route_request_to_endpoint_if_it_does_not_match(self):
        class Hello(Endpoint):
            endpoint_path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/world'}
        start_response = Mock()
        body = app(env, start_response)
        start_response.assert_called_once_with('404 Not Found', {'Content-Type': 'text/plain; charset=utf-8'}.items())
        self.assertEqual(body, (b'',))
