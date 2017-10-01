from unittest import TestCase
from unittest.mock import Mock

from gatekeeper import Request, JsonRequest, JsonEndpoint


class JsonEndpointTestCase(TestCase):

    def test_request_gets_converted_to_json_request_inside_endpoint(self):
        class JsonTestEndpoint(JsonEndpoint):
            endpoint_path = '/'
            def get(self, request, response):
                assert isinstance(request, JsonRequest)
        endpoint = JsonTestEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)

    def test_response_has_correct_content_type(self):
        endpoint = JsonEndpoint()
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.headers['Content-Type'], 'application/json; charset=utf-8')

    def test_response_json_gets_dumped_to_body(self):
        class JsonTestEndpoint(JsonEndpoint):
            endpoint_path = '/'
            def get(self, request, response):
                response.json = {'ok': True}
        endpoint = JsonTestEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'{"ok": true}')

    def test_default_json_response_is_empty_object(self):
        endpoint = JsonEndpoint()
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.body, b'{}')
