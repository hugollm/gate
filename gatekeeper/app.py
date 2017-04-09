from .requests.request import Request
from .responses.response import Response


class App(object):

    def __init__(self):
        self.endpoints = []

    def endpoint(self, endpoint_class):
        self.endpoints.append(endpoint_class())

    def __call__(self, env, start_response):
        request = Request(env)
        response = self.handle_request(request)
        return response.wsgi(start_response)

    def handle_request(self, request):
        response = self._try_to_get_response_from_an_endpoint(request)
        if response is None:
            response = self._response_404()
        return response

    def _try_to_get_response_from_an_endpoint(self, request):
        for endpoint in self.endpoints:
            if endpoint.match_request(request):
                return endpoint.handle_request(request)
        return None

    def _response_404(self):
        response = Response()
        response.status = 404
        return response
