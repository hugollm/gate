from ..responses.response import Response


class Endpoint(object):

    def match_request(self, request):
        url_match = self.endpoint_path == request.path
        method_match = hasattr(self, request.method.lower())
        return url_match and method_match

    def handle_request(self, request):
        response = Response()
        method = getattr(self, request.method.lower())
        if hasattr(self, 'before_request'):
            self.before_request(request, response)
        method(request, response)
        return response
