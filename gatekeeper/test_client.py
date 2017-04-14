import copy
import json
import mimetypes
import urllib
from http.cookies import SimpleCookie
import os.path
from io import BytesIO

from .requests.request import Request


class TestClient(object):

    def __init__(self, app):
        self.app = app
        self.cookies = []

    def get(self, path, query=None, form=None, json=None):
        return self.request('GET', path, query, form, None, json)

    def post(self, path, query=None, form=None, files=None, json=None):
        return self.request('POST', path, query, form, files, json)

    def put(self, path, query=None, form=None, files=None, json=None):
        return self.request('PUT', path, query, form, files, json)

    def patch(self, path, query=None, form=None, files=None, json=None):
        return self.request('PATCH', path, query, form, files, json)

    def delete(self, path, query=None, form=None, json=None):
        return self.request('DELETE', path, query, form, None, json)

    def head(self, path, query=None, form=None, json=None):
        return self.request('HEAD', path, query, form, None, json)

    def options(self, path, query=None, form=None, json=None):
        return self.request('OPTIONS', path, query, form, None, json)

    def request(self, method, path, query=None, form=None, files=None, json=None):
        request = self._make_request(method, path, query, form, files, json)
        response = self.app.handle_request(request)
        self.cookies.extend(response.cookies)
        return response

    def _make_request(self, method, path, query, form, files, json_data):
        env = copy.deepcopy(sample_env)
        env['REQUEST_METHOD'] = method.upper()
        env['PATH_INFO'] = path
        if query:
            env['QUERY_STRING'] = urllib.parse.urlencode(query)
        if form and not files:
            self._write_form_to_env(env, form)
        if files:
            self._write_multipart_form_to_env(env, form, files)
        if json_data:
            env['wsgi.input'].write(json.dumps(json_data).encode('utf-8'))
            env['wsgi.input'].seek(0)
        if self.cookies:
            env['HTTP_COOKIE'] = self._assemble_cookie_string()
        return Request(env)

    def _write_form_to_env(self, env, form):
        items = []
        for key, value in form.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                for v in value:
                    item = urllib.parse.urlencode({key: v})
                    items.append(item)
            else:
                item = urllib.parse.urlencode({key: value})
                items.append(item)
        env['wsgi.input'].write('&'.join(items).encode('utf-8'))
        env['wsgi.input'].seek(0)

    def _write_multipart_form_to_env(self, env, form, files):
        bytecount = 0
        env['CONTENT_TYPE'] = 'multipart/form-data; boundary=----WebKitFormBoundaryLn6U80VApiAoyY3B'
        bytecount += self._write_multipart_data_to_env(env, form)
        bytecount += self._write_multipart_files_to_env(env, files)
        bytecount += env['wsgi.input'].write(b'------WebKitFormBoundaryLn6U80VApiAoyY3B--\n')
        env['CONTENT_LENGTH'] = str(bytecount)
        env['wsgi.input'].seek(0)

    def _write_multipart_data_to_env(self, env, form):
        bytecount = 0
        if form:
            for key, value in form.items():
                if hasattr(value, '__iter__') and not isinstance(value, str):
                    for v in value:
                        bytecount += env['wsgi.input'].write(b'------WebKitFormBoundaryLn6U80VApiAoyY3B\n')
                        bytecount += env['wsgi.input'].write('Content-Disposition: form-data; name="{}"\n\n'.format(key).encode('utf-8'))
                        bytecount += env['wsgi.input'].write(str(v).encode('utf-8') + b'\n')
                else:
                    bytecount += env['wsgi.input'].write(b'------WebKitFormBoundaryLn6U80VApiAoyY3B\n')
                    bytecount += env['wsgi.input'].write('Content-Disposition: form-data; name="{}"\n\n'.format(key).encode('utf-8'))
                    bytecount += env['wsgi.input'].write(str(value).encode('utf-8') + b'\n')
        return bytecount

    def _write_multipart_files_to_env(self, env, files):
        bytecount = 0
        for key, filepath in files.items():
            filename = os.path.basename(filepath)
            mime_type, _ = mimetypes.guess_type(filepath)
            if not mime_type:
                mime_type = 'application/octet-stream'
            with open(filepath, 'rb') as f:
                bytecount += env['wsgi.input'].write(b'------WebKitFormBoundaryLn6U80VApiAoyY3B\n')
                bytecount += env['wsgi.input'].write('Content-Disposition: form-data; name="{}"; filename="{}"\n'.format(key, filename).encode('utf-8'))
                bytecount += env['wsgi.input'].write('Content-Type: {}\n\n'.format(mime_type).encode('utf-8'))
                bytecount += env['wsgi.input'].write(f.read() + b'\n')
        return bytecount

    def _assemble_cookie_string(self):
        simple_cookie = SimpleCookie()
        for cookie in self.cookies:
            simple_cookie.load(cookie)
        cookie_dict = {key: simple_cookie[key].value for key in simple_cookie}
        cookie_string = ''
        for morsel in SimpleCookie(cookie_dict).values():
            if morsel.value != '':
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
