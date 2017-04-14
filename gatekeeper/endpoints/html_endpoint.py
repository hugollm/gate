from .endpoint import Endpoint
from ..requests.html_request import HtmlRequest
from ..responses.html_response import HtmlResponse


class HtmlEndpoint(Endpoint):

    def __init__(self):
        super(HtmlEndpoint, self).__init__()
        self.jinja_env = None

    def _make_response(self):
        response = HtmlResponse()
        if self.jinja_env:
            response.jinja_env = self.jinja_env
        return response

    def handle_request(self, request):
        request = HtmlRequest(request.env)
        return super(HtmlEndpoint, self).handle_request(request)
