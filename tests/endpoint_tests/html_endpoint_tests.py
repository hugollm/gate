from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.requests.request import Request
from gatekeeper.requests.html_request import HtmlRequest
from gatekeeper.endpoints.html_endpoint import HtmlEndpoint


class HtmlEndpointTestCase(TestCase):

    def test_request_gets_converted_to_html_request_inside_endpoint(self):
        class HtmlTestEndpoint(HtmlEndpoint):
            endpoint_path = '/'
            def get(self, request, response):
                assert isinstance(request, HtmlRequest)
        endpoint = HtmlTestEndpoint()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)

    def test_response_has_correct_content_type(self):
        endpoint = HtmlEndpoint()
        endpoint.get = Mock()
        request = Request({'REQUEST_METHOD': 'GET', 'PATH_INFO': '/'})
        response = endpoint.handle_request(request)
        self.assertEqual(response.headers['Content-Type'], 'text/html; charset=utf-8')
