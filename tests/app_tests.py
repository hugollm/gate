from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.app import App, DuplicateEndpoints, AmbiguousEndpoints
from gatekeeper.endpoints.endpoint import Endpoint


class AppTestCase(TestCase):

    def test_app_without_endpoints_responds_with_404(self):
        app = App()
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'}
        start_response = Mock()
        body = app(env, start_response)
        start_response.assert_called_once_with('404 Not Found', list({'Content-Type': 'text/plain; charset=utf-8'}.items()))
        self.assertEqual(body, (b'',))

    def test_app_routes_request_to_endpoint_if_it_matches(self):
        class Hello(Endpoint):
            path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/hello'}
        start_response = Mock()
        body = app(env, start_response)
        start_response.assert_called_once_with('200 OK', list({'Content-Type': 'text/plain; charset=utf-8'}.items()))
        self.assertEqual(body, (b'hello world',))

    def test_app_does_not_route_request_to_endpoint_if_it_does_not_match(self):
        class Hello(Endpoint):
            path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/world'}
        start_response = Mock()
        body = app(env, start_response)
        start_response.assert_called_once_with('404 Not Found', list({'Content-Type': 'text/plain; charset=utf-8'}.items()))
        self.assertEqual(body, (b'',))

    def test_app_raises_if_two_endpoints_with_exactly_the_same_path_are_registered(self):
        class Hello1(Endpoint):
            path = '/hello'
            def get(self, request, response):
                pass
        class Hello2(Endpoint):
            path = '/hello'
            def get(self, request, response):
                pass
        app = App()
        app.endpoint(Hello1)
        with self.assertRaises(DuplicateEndpoints):
            app.endpoint(Hello2)

    def test_app_raises_if_a_path_lead_to_more_than_one_endpoint(self):
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
