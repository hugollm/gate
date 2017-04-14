from .requests.request import Request
from .responses.response import Response
from .exceptions import DuplicateEndpoints, AmbiguousEndpoints, JinjaEnvNotSet


class App(object):

    def __init__(self):
        self.endpoints = []
        self.paths = set()
        self.jinja_env = None

    def set_jinja_env(self, package_map):
        from jinja2 import Environment, PrefixLoader, PackageLoader
        loader_map = {}
        for package, directory in package_map.items():
            loader_map[package] = PackageLoader(package, directory)
        self.jinja_env = Environment(loader=PrefixLoader(loader_map))

    def render(self, template_identifier, context=None):
        from jinja2 import Template
        if self.jinja_env is None:
            raise JinjaEnvNotSet()
        template = self.jinja_env.get_template(template_identifier)
        context = context or {}
        context.pop('self', None)
        return template.render(**context)

    def endpoint(self, endpoint_class):
        endpoint = endpoint_class()
        if endpoint.path in self.paths:
            raise DuplicateEndpoints(endpoint.path)
        self.paths.add(endpoint.path)
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
        matched_endpoints = []
        for endpoint in self.endpoints:
            if endpoint.match_request(request):
                matched_endpoints.append(endpoint)
        if len(matched_endpoints) > 1:
            raise AmbiguousEndpoints(request.path)
        elif matched_endpoints:
            endpoint = matched_endpoints.pop()
            return endpoint.handle_request(request)
        return None

    def _response_404(self):
        response = Response()
        response.status = 404
        return response
