from ..responses.response import Response


class Endpoint(object):

    def match_request(self, request):
        url_match = self.endpoint_path == request.path
        method_match = hasattr(self, request.method.lower())
        return url_match and method_match

    def handle_request(self, request):
        response = Response()
        method = getattr(self, request.method.lower())
        method(request, response)
        return response
