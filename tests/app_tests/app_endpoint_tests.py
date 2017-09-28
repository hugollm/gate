from unittest.mock import Mock

from .app_test_case import AppTestCase

from gatekeeper.app import App
from gatekeeper.endpoints.endpoint import Endpoint
from gatekeeper.exceptions import AmbiguousEndpoints


class AppEndpointTestCase(AppTestCase):

    def test_app_without_endpoints_responds_with_404(self):
        app = App()
        expected_status = '404 Not Found'
        expected_headers = {'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': '0'}
        expected_body = b''
        self.assert_call(app, 'GET', '/', expected_status, expected_headers, expected_body)

    def test_app_routes_request_to_endpoint_if_it_matches(self):
        class Hello(Endpoint):
            path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': '11'}
        expected_body = b'hello world'
        self.assert_call(app, 'GET', '/hello', expected_status, expected_headers, expected_body)

    def test_app_does_not_route_request_to_endpoint_if_it_does_not_match(self):
        class Hello(Endpoint):
            path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        expected_status = '404 Not Found'
        expected_headers = {'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': '0'}
        expected_body = b''
        self.assert_call(app, 'GET', '/world', expected_status, expected_headers, expected_body)

    def test_app_allows_two_endpoints_with_the_same_path_if_the_method_is_different(self):
        class Hello1(Endpoint):
            path = '/hello'
            def get(self, request, response):
                pass
        class Hello2(Endpoint):
            path = '/hello'
            def post(self, request, response):
                pass
        app = App()
        app.endpoint(Hello1)
        app.endpoint(Hello2)
        self.assert_call(app, 'GET', '/hello', '200 OK')

    def test_app_raises_if_a_request_leads_to_more_than_one_endpoint(self):
        class User1(Endpoint):
            path = '/users/:id'
            def get(self, request, response):
                pass
        class User2(Endpoint):
            path = '/users/:userid'
            def get(self, request, response):
                pass
        app = App()
        app.endpoint(User1)
        app.endpoint(User2)
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9'}
        start_response = Mock()
        with self.assertRaises(AmbiguousEndpoints):
            app(env, start_response)
