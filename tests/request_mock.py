from io import BytesIO
from gateway.request import Request


class RequestMock(Request):

    def __init__(self):
        super(RequestMock, self).__init__({
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
        })

    @property
    def method(self):
        return super(RequestMock, self).method

    @property
    def scheme(self):
        return super(RequestMock, self).scheme

    @property
    def host(self):
        return super(RequestMock, self).host

    @property
    def path(self):
        return super(RequestMock, self).path

    @property
    def query_string(self):
        return super(RequestMock, self).query_string

    @property
    def body(self):
        return super(RequestMock, self).body

    @method.setter
    def method(self, method):
        self.env['REQUEST_METHOD'] = method

    @scheme.setter
    def scheme(self, scheme):
        self.env['wsgi.url_scheme'] = scheme

    @host.setter
    def host(self, host):
        self.env['HTTP_HOST'] = host

    @path.setter
    def path(self, path):
        self.env['PATH_INFO'] = path

    @query_string.setter
    def query_string(self, query_string):
        self.env['QUERY_STRING'] = query_string

    @body.setter
    def body(self, body):
        self.env['wsgi.input'] = BytesIO()
        self.env['wsgi.input'].write(body)
        self.env['wsgi.input'].seek(0)
        self._body = None
