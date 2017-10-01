from .endpoint import Endpoint
from ..requests.html_request import HtmlRequest
from ..responses.html_response import HtmlResponse


class HtmlEndpoint(Endpoint):

    def _make_response(self):
        return HtmlResponse()

    def handle_request(self, request):
        request = HtmlRequest(request.env)
        return super(HtmlEndpoint, self).handle_request(request)
