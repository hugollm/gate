import copy
import json
import urllib
from http.cookies import SimpleCookie
from io import BytesIO

from .requests.request import Request


class TestClient(object):

    def __init__(self, app):
        self.app = app
        self.cookies = []

    def get(self, path, query=None, form=None, json=None):
        return self.request('GET', path, query, form, json)

    def post(self, path, query=None, form=None, json=None):
        return self.request('POST', path, query, form, json)

    def put(self, path, query=None, form=None, json=None):
        return self.request('PUT', path, query, form, json)

    def patch(self, path, query=None, form=None, json=None):
        return self.request('PATCH', path, query, form, json)

    def delete(self, path, query=None, form=None, json=None):
        return self.request('DELETE', path, query, form, json)

    def head(self, path, query=None, form=None, json=None):
        return self.request('HEAD', path, query, form, json)

    def options(self, path, query=None, form=None, json=None):
        return self.request('OPTIONS', path, query, form, json)

    def request(self, method, path, query=None, form=None, json=None):
        request = self._make_request(method, path, query, form, json)
        response = self.app.handle_request(request)
        self.cookies.extend(response.cookies)
        return response

    def _make_request(self, method, path, query, form, json_data):
        env = copy.deepcopy(sample_env)
        env['REQUEST_METHOD'] = method.upper()
        env['PATH_INFO'] = path
        if query:
            env['QUERY_STRING'] = urllib.parse.urlencode(query)
        if form:
            env['wsgi.input'].write(urllib.parse.urlencode(form).encode('utf-8'))
            env['wsgi.input'].seek(0)
        if json_data:
            env['wsgi.input'].write(json.dumps(json_data).encode('utf-8'))
            env['wsgi.input'].seek(0)
        if self.cookies:
            env['HTTP_COOKIE'] = self._assemble_cookie_string()
        return Request(env)

    def _assemble_cookie_string(self):
        simple_cookie = SimpleCookie()
        for cookie in self.cookies:
            simple_cookie.load(cookie)
        cookie_dict = {key: simple_cookie[key].value for key in simple_cookie}
        cookie_dict.pop('SameSite', None) # sazonal bug with SameSite
        cookie_string = ''
        for morsel in SimpleCookie(cookie_dict).values():
            cookie_string += morsel.OutputString() + '; '
        cookie_string = cookie_string[:-2]
        return cookie_string


sample_env = {
    'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'HTTP_ACCEPT_ENCODING': 'gzip, deflate, sdch',
    'HTTP_ACCEPT_LANGUAGE': 'pt-BR,pt;q=0.8,en-US;q=0.6,en;q=0.4',
    'HTTP_CONNECTION': 'keep-alive',
    'HTTP_HOST': 'localhost:8000',
    'HTTP_UPGRADE_INSECURE_REQUESTS': '1',
    'HTTP_USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
    'PATH_INFO': '',
    'QUERY_STRING': '',
    'RAW_URI': '',
    'REMOTE_ADDR': '127.0.0.1',
    'REMOTE_PORT': '54130',
    'REQUEST_METHOD': 'GET',
    'SCRIPT_NAME': '',
    'SERVER_NAME': '127.0.0.1',
    'SERVER_PORT': '8000',
    'SERVER_PROTOCOL': 'HTTP/1.1',
    'SERVER_SOFTWARE': 'gunicorn/19.6.0',
    'wsgi.errors': BytesIO(),
    'wsgi.file_wrapper': BytesIO(),
    'wsgi.input': BytesIO(),
    'wsgi.multiprocess': False,
    'wsgi.multithread': False,
    'wsgi.run_once': False,
    'wsgi.url_scheme': 'http',
    'wsgi.version': (1, 0),
}
