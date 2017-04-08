from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.requests.request import Request
from gatekeeper.responses.response import Response
from gatekeeper.endpoints.endpoint import Endpoint
from . import endpoints


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

    def test_simple_get_request(self):
        endpoint = endpoints.SimpleGet()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, b'hello world')
