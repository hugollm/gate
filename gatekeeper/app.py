from importlib import import_module
from inspect import getmembers, isclass
from pkgutil import walk_packages, iter_modules
import os.path

from .requests.request import Request
from .responses.response import Response
from .responses.html_response import HtmlResponse
from .endpoints.endpoint import Endpoint
from .exceptions import AmbiguousEndpoints, InvalidDirectory
from .template_renderer import TemplateRenderer


class App(object):

    def __init__(self):
        self.endpoints = []
        self.registered_endpoint_classes = set()
        self.static_paths = []
        self.template_renderer = TemplateRenderer()

    def endpoint(self, endpoint_class):
        if endpoint_class in self.registered_endpoint_classes:
            return
        endpoint = endpoint_class()
        endpoint.template_renderer = self.template_renderer
        self.endpoints.append(endpoint)
        self.registered_endpoint_classes.add(endpoint_class)

    def static(self, path):
        if not os.path.isdir(path):
            raise InvalidDirectory(path)
        self.static_paths.append(path)

    def pages(self, path):
        if not os.path.isdir(path):
            raise InvalidDirectory(path)
        self.template_renderer.add_directory(path)

    def package(self, path):
        self._register_package_endpoints(path)
        self.template_renderer.add_package(path)

    def _register_package_endpoints(self, package_path):
        package = import_module(package_path)
        for loader, module_path, is_package in walk_packages(package.__path__):
            module = import_module('.' + module_path, package_path)
            if is_package:
                self._register_package_endpoints(module.__name__)
            else:
                classes = getmembers(module, isclass)
                for class_name, cls in classes:
                    if issubclass(cls, Endpoint) and cls.__module__.startswith(package_path):
                        self.endpoint(cls)

    def __call__(self, env, start_response):
        request = Request(env)
        response = self.handle_request(request)
        self._try_rendering_status_page(response)
        return response.wsgi(start_response)

    def handle_request(self, request):
        response = self._try_response_for_static_file(request)
        if response:
            return response
        response = self._try_response_from_page(request)
        if response:
            return response
        response = self._try_response_from_an_endpoint(request)
        if response:
            return response
        return self._response_404()

    def _try_response_for_static_file(self, request):
        for base_path in self.static_paths:
            path = os.path.join(base_path, request.path.lstrip('/'))
            if os.path.isfile(path):
                response = Response()
                response.file(path)
                return response
        return None

    def _try_response_from_page(self, request):
        page = request.path.strip('/')
        if os.path.basename(page) == 'index':
            return None # index pages should not be referenced explicitly
        regular_template_path = page + '.html' if page else None
        index_template_path = (page + '/index.html').strip('/')
        for template_path in (regular_template_path, index_template_path):
            if template_path and self.template_renderer.has_page(template_path):
                response = Response()
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
                response.body = self.template_renderer.render(template_path)
                return response
        return None

    def _try_response_from_an_endpoint(self, request):
        matched_endpoints = []
        for endpoint in self.endpoints:
            if endpoint.match_request(request):
                matched_endpoints.append(endpoint)
        if len(matched_endpoints) > 1:
            raise AmbiguousEndpoints(request)
        elif matched_endpoints:
            endpoint = matched_endpoints.pop()
            return endpoint.handle_request(request)
        return None

    def _response_404(self):
        response = HtmlResponse()
        response.status = 404
        return response

    def _try_rendering_status_page(self, response):
        if isinstance(response, HtmlResponse) and not response.body:
            template_path = str(response.status) + '.html'
            if self.template_renderer.has_page(template_path):
                response.body = self.template_renderer.render(template_path)
        return None
