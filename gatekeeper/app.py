from .requests.request import Request
from .responses.response import Response


class App(object):

    def __init__(self):
        self.endpoints = []

    def endpoint(self, endpoint_class):
        self.endpoints.append(endpoint_class())

    def __call__(self, env, start_response):
        request = Request(env)
        response = self.try_to_get_response_from_an_endpoint(request)
        if response is None:
            response = self.response_404()
        return response.wsgi(start_response)

    def try_to_get_response_from_an_endpoint(self, request):
        for endpoint in self.endpoints:
            if endpoint.match_request(request):
                return endpoint.handle_request(request)
        return None

    def response_404(self):
        response = Response()
        response.status = 404
        return response
