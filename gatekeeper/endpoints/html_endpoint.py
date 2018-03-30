from .endpoint import Endpoint
from ..requests.html_request import HtmlRequest
from ..responses.html_response import HtmlResponse


class HtmlEndpoint(Endpoint):

    def _make_response(self):
        return HtmlResponse()

    def handle_request(self, request):
        request = HtmlRequest(request.env)
        return super(HtmlEndpoint, self).handle_request(request)

    def _execute_life_cycle(self, request, response):
        request.response = response
        return super(HtmlEndpoint, self)._execute_life_cycle(request, response)
