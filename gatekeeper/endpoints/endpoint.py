import re
from ..responses.response import Response


class Endpoint(object):

    path = None
    _allowed_methods = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS')

    def __init__(self):
        self._compiled_regex = None
        self._compile_regex_if_needed()

    def _compile_regex_if_needed(self):
        regex = self._path_regex()
        if regex:
            self._compiled_regex = re.compile(regex)

    def _path_regex(self):
        if self._path_is_regex():
            return self.path
        elif self._path_is_simple_pattern():
            return self._simple_pattern_to_regex(self.path)
        else:
            return None

    def _path_is_simple_pattern(self):
        return (
            self.path and
            not self._path_is_regex() and
            re.match(r'.*\/:[^\/]+.*', self.path)
        )

    def _path_is_regex(self):
        return self.path and self.path.startswith('^')

    def _simple_pattern_to_regex(self, pattern):
        return '^' + re.sub(r'\/:([^\/]+)', r'/(?P<\1>[^\/]+)', self.path) + '$'

    def match_request(self, request):
        return self._url_match(request) and self._method_match(request)

    def _url_match(self, request):
        if self._compiled_regex:
            return self._compiled_regex.match(request.path)
        return request.path == self.path

    def _method_match(self, request):
        is_allowed = request.method in self._allowed_methods
        has_method = hasattr(self, request.method.lower())
        return is_allowed and has_method

    def handle_request(self, request):
        self._fill_request_args(request)
        response = self._make_response()
        request.set_response(response)
        self._execute_life_cycle(request, response)
        return response

    def _fill_request_args(self, request):
        request.args = {}
        if self._compiled_regex:
            match = self._compiled_regex.match(request.path)
            request.args = match.groupdict()

    def _make_response(self):
        return Response()

    def _execute_life_cycle(self, request, response):
        method = getattr(self, request.method.lower())
        try:
            if hasattr(self, 'before_request'):
                self.before_request(request, response)
            if request.method in self._allowed_methods:
                method(request, response)
        except Response:
            pass
        except Exception as e:
            if hasattr(self, 'on_exception'):
                self.on_exception(request, e)
            raise
        try:
            if hasattr(self, 'after_request'):
                self.after_request(request, response)
        except Response:
            pass
        except Exception as e:
            if hasattr(self, 'on_exception'):
                self.on_exception(request, e)
            raise
