from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.requests.request import Request
from gatekeeper.responses.response import Response
from gatekeeper.endpoints.endpoint import Endpoint


class EndpointTestCase(TestCase):

    def test_endpoint_match_request_when_url_and_method_are_compatible(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/'
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        self.assertTrue(endpoint.match_request(request))

    def test_endpoint_does_not_match_request_when_url_is_incompatible(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/'
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/foo'})
        self.assertFalse(endpoint.match_request(request))

    def test_endpoint_does_not_match_request_when_method_is_incompatible(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/'
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'POST', 'PATH_INFO': '/'})
        self.assertFalse(endpoint.match_request(request))

    def test_endpoint_handle_request_returns_response(self):
        endpoint = Endpoint()
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertIsInstance(response, Response)

    def test_endpoint_method_can_change_response(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/'
        def get(self, request, response):
            response.body = b'hello world'
        endpoint.get = get.__get__(self, endpoint)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_endpoint_calls_before_request_method_if_defined(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/'
        def before_request(self, request, response):
            response.body = b'hello'
        def get(self, request, response):
            response.body += b' world'
        endpoint.before_request = before_request.__get__(self, endpoint)
        endpoint.get = get.__get__(self, endpoint)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_endpoint_calls_before_request_method_if_defined(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/'
        def get(self, request, response):
            response.body = b'hello'
        def after_request(self, request, response):
            response.body += b' world'
        endpoint.get = get.__get__(self, endpoint)
        endpoint.after_request = after_request.__get__(self, endpoint)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_endpoint_path_pattern(self):
        endpoint = Endpoint()
        endpoint.endpoint_path = '/users/:id'
        self.assertEqual(endpoint._path_pattern(), r'^/users/(?P<id>[^\/]+)$')

    def test_endpoint_match_request_with_url_args_if_path_matches_the_pattern_exactly(self):
        class ArgsEndpoint(Endpoint):
            endpoint_path = '/users/:id'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9'})
        self.assertTrue(endpoint.match_request(request))

    def test_endpoint_does_not_match_request_with_url_args_if_path_only_contains_the_pattern(self):
        class ArgsEndpoint(Endpoint):
            endpoint_path = '/users/:id'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9/edit'})
        self.assertFalse(endpoint.match_request(request))

    def test_endpoint_url_args_are_available_in_request_object(self):
        class ArgsEndpoint(Endpoint):
            endpoint_path = '/users/:id/:username/edit'
            def get(self, request, response):
                response.args = request.args
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9/john/edit'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.args, {'id': '9', 'username': 'john'})

    def test_endpoint_without_arguments_have_empty_dict_as_args(self):
        class ArgsEndpoint(Endpoint):
            endpoint_path = '/users'
            def get(self, request, response):
                response.args = request.args
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.args, {})
