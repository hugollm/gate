import re
from ..responses.response import Response


class Endpoint(object):

    path = None

    def __init__(self):
        self._compiled_path_pattern = None
        if self.path and ':' in self.path:
            self._compiled_path_pattern = re.compile(self._path_pattern())

    def _path_pattern(self):
        pattern = re.sub(r'\/:([^\/]+)', r'/(?P<\1>[^\/]+)', self.path)
        return '^' + pattern + '$'

    def match_request(self, request):
        return self._url_match(request) and self._method_match(request)

    def _url_match(self, request):
        if self._compiled_path_pattern:
            return self._compiled_path_pattern.match(request.path)
        return request.path == self.path

    def _method_match(self, request):
        return hasattr(self, request.method.lower())

    def handle_request(self, request):
        self._fill_request_args(request)
        response = self._make_response()
        request.set_response(response)
        self._execute_life_cycle(request, response)
        return response

    def _fill_request_args(self, request):
        request.args = {}
        if self._compiled_path_pattern:
            match = self._compiled_path_pattern.match(request.path)
            request.args = match.groupdict()

    def _make_response(self):
        return Response()

    def _execute_life_cycle(self, request, response):
        method = getattr(self, request.method.lower())
        try:
            if hasattr(self, 'before_request'):
                self.before_request(request, response)
            method(request, response)
            if hasattr(self, 'after_request'):
                self.after_request(request, response)
        except Response:
            pass
