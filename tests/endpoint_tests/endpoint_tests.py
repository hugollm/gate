from unittest import TestCase
from unittest.mock import Mock

from gate.requests.request import Request
from gate.responses.response import Response
from gate.endpoints.endpoint import Endpoint


class EndpointTestCase(TestCase):

    def test_endpoint_match_request_when_url_and_method_are_compatible(self):
        endpoint = Endpoint()
        endpoint.path = '/'
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        self.assertTrue(endpoint.match_request(request))

    def test_endpoint_does_not_match_request_when_url_is_incompatible(self):
        endpoint = Endpoint()
        endpoint.path = '/'
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/foo'})
        self.assertFalse(endpoint.match_request(request))

    def test_endpoint_does_not_match_request_when_method_is_incompatible(self):
        endpoint = Endpoint()
        endpoint.path = '/'
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
        endpoint.path = '/'
        def get(self, request, response):
            response.body = b'hello world'
        endpoint.get = get.__get__(self, endpoint)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_endpoint_calls_before_request_method_if_defined(self):
        endpoint = Endpoint()
        endpoint.path = '/'
        def before_request(self, request, response):
            response.body = b'hello'
        def get(self, request, response):
            response.body += b' world'
        endpoint.before_request = before_request.__get__(self, endpoint)
        endpoint.get = get.__get__(self, endpoint)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_endpoint_calls_after_request_method_if_defined(self):
        endpoint = Endpoint()
        endpoint.path = '/'
        def get(self, request, response):
            response.body = b'hello'
        def after_request(self, request, response):
            response.body += b' world'
        endpoint.get = get.__get__(self, endpoint)
        endpoint.after_request = after_request.__get__(self, endpoint)
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_path_regex_when_path_is_simple_pattern(self):
        endpoint = Endpoint()
        endpoint.path = '/users/:id'
        self.assertEqual(endpoint._path_regex(), r'^/users/(?P<id>[^\/]+)$')

    def test_path_regex_when_path_is_explicit_regex(self):
        endpoint = Endpoint()
        endpoint.path = r'^/static/(?P<path>.+)$'
        self.assertEqual(endpoint._path_regex(), r'^/static/(?P<path>.+)$')

    def test_path_regex_that_contains_colon_does_not_get_confused_with_simple_pattern(self):
        endpoint = Endpoint()
        endpoint.path = r'^/users/:id'
        self.assertEqual(endpoint._path_regex(), r'^/users/:id')

    def test_endpoint_match_request_with_url_args_if_path_matches_the_pattern_exactly(self):
        class ArgsEndpoint(Endpoint):
            path = '/users/:id'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9'})
        self.assertTrue(endpoint.match_request(request))

    def test_endpoint_does_not_match_request_with_url_args_if_path_only_contains_the_pattern(self):
        class ArgsEndpoint(Endpoint):
            path = '/users/:id'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9/edit'})
        self.assertFalse(endpoint.match_request(request))

    def test_endpoint_match_request_with_explicit_regex(self):
        class ArgsEndpoint(Endpoint):
            path = r'^/static/(?P<path>.+)$'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/static/css/styles.css'})
        self.assertTrue(endpoint.match_request(request))

    def test_endpoint_match_does_not_confuse_simple_pattern_with_explicit_regex(self):
        class ArgsEndpoint(Endpoint):
            path = r'^/users/:id'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9'})
        self.assertFalse(endpoint.match_request(request))

    def test_endpoint_url_args_are_available_in_request_object(self):
        class ArgsEndpoint(Endpoint):
            path = '/users/:id/:username/edit'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users/9/john/edit'})
        response = endpoint.handle_request(request)
        self.assertEqual(request.args, {'id': '9', 'username': 'john'})

    def test_endpoint_without_arguments_have_empty_dict_as_args(self):
        class ArgsEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                pass
        endpoint = ArgsEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        response = endpoint.handle_request(request)
        self.assertEqual(request.args, {})

    def test_endpoint_can_handle_raised_responses(self):
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                raise response
        endpoint = RaiseEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        response = endpoint.handle_request(request)
        self.assertIsInstance(response, Response)

    def test_raising_response_on_before_request_jumps_main_method(self):
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def before_request(self, request, response):
                response.body = b'hello'
                raise response
            def get(self, request, response):
                response.body += b' world'
        endpoint = RaiseEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello')

    def test_raising_response_on_main_method_does_not_jump_after_request(self):
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                response.body = b'hello'
                raise response
            def after_request(self, request, response):
                response.body += b' world'
        endpoint = RaiseEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_after_request_method_can_raise_response(self):
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                response.body = b'hello'
            def after_request(self, request, response):
                response.body += b' world'
                raise response
        endpoint = RaiseEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'hello world')

    def test_endpoint_sets_response_in_request(self):
        class SetResponseEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                assert isinstance(request.response, Response)
        endpoint = SetResponseEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        endpoint.handle_request(request)

    def test_on_exception_method_gets_called_if_an_unexpected_exception_raises(self):
        class CustomException(Exception):
            pass
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                raise CustomException()
        endpoint = RaiseEndpoint()
        endpoint.on_exception = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        with self.assertRaises(CustomException) as context:
            endpoint.handle_request(request)
        endpoint.on_exception.assert_called_once_with(request, context.exception)

    def test_on_exception_method_gets_called_exception_raises_in_before_request(self):
        class CustomException(Exception):
            pass
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def before_request(self, request, response):
                raise CustomException()
            def get(self, request, response):
                pass
        endpoint = RaiseEndpoint()
        endpoint.on_exception = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        with self.assertRaises(CustomException) as context:
            endpoint.handle_request(request)
        endpoint.on_exception.assert_called_once_with(request, context.exception)

    def test_on_exception_method_gets_called_exception_raises_in_after_request(self):
        class CustomException(Exception):
            pass
        class RaiseEndpoint(Endpoint):
            path = '/users'
            def get(self, request, response):
                pass
            def after_request(self, request, response):
                raise CustomException()
        endpoint = RaiseEndpoint()
        endpoint.on_exception = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/users'})
        with self.assertRaises(CustomException) as context:
            endpoint.handle_request(request)
        endpoint.on_exception.assert_called_once_with(request, context.exception)

    def test_endpoint_accepted_methods(self):
        endpoint = Endpoint()
        endpoint.path = '/'
        allowed_methods = ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
        for method in allowed_methods:
            setattr(endpoint, method, Mock())
            request = Request({'REQUEST_METHOD': method.upper(), 'PATH_INFO': '/'})
            self.assertTrue(endpoint.match_request(request))
            endpoint.handle_request(request)
            self.assertEqual(getattr(endpoint, method).call_count, 1)

    def test_endpoint_rejects_invalid_method(self):
        endpoint = Endpoint()
        endpoint.path = '/'
        endpoint.foobar = Mock()
        request = Request({'REQUEST_METHOD': 'FOOBAR', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertFalse(endpoint.match_request(request))
        self.assertEqual(endpoint.foobar.call_count, 0)
