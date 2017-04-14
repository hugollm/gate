from unittest import TestCase
from unittest.mock import Mock

from jinja2 import Environment

from gatekeeper.app import App
from gatekeeper.endpoints.endpoint import Endpoint
from gatekeeper.exceptions import DuplicateEndpoints, AmbiguousEndpoints, JinjaEnvNotSet


class AppTestCase(TestCase):

    def assert_call(self, app, method, path, expected_status=None, expected_headers=None, expected_body=None):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': path}
        start_response = Mock()
        body = app(env, start_response)
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

    def test_set_jinja_env(self):
        app = App()
        app.set_jinja_env({'tests.app_tests.hello': 'templates'})
        self.assertIsInstance(app.jinja_env, Environment)

    def test_render(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        text = app.render('tests.app_tests.hello/hello.html', {'name': 'John'})
        self.assertEqual(text, '<body><h1>Hello John</h1></body>')

    def test_render_can_be_called_without_context(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        text = app.render('tests.app_tests.hello/hello.html')
        self.assertEqual(text, '<body><h1>Hello </h1></body>')

    def test_render_can_be_called_with_locals_as_context(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        name = 'John'
        text = app.render('tests.app_tests.hello/hello.html', locals())
        self.assertEqual(text, '<body><h1>Hello John</h1></body>')

    def test_calling_render_without_setting_jinja_env_raises_exception(self):
        app = App()
        with self.assertRaises(JinjaEnvNotSet):
            app.render('tests.app_tests.hello/hello.html')