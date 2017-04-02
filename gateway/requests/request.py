from http.cookies import SimpleCookie
from urllib.parse import parse_qsl


class Request(object):

    def __init__(self, env):
        self.env = env
        self._body = None
        self._query = None
        self._headers = None
        self._cookies = None

    @property
    def method(self):
        return self.env['REQUEST_METHOD']

    @property
    def url(self):
        url = self.scheme + '://' + self.host + self.path
        if self.query_string:
            url += '?' + self.query_string
        return url

    @property
    def scheme(self):
        return self.env['wsgi.url_scheme']

    @property
    def host(self):
        return self.env['HTTP_HOST']

    @property
    def path(self):
        return self.env['PATH_INFO']

    @property
    def query_string(self):
        return self.env['QUERY_STRING']

    @property
    def query(self):
        if self._query is None:
            self._query = dict(parse_qsl(self.query_string, keep_blank_values=True))
        return self._query

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {}
            for key, value in self.env.items():
                if key.startswith('HTTP_'):
                    new_key = key[5:].lower().replace('_', '-')
                    self._headers[new_key] = value
        return self._headers

    @property
    def cookies(self):
        if self._cookies is None:
            cookie_string = self.env.get('HTTP_COOKIE')
            if cookie_string:
                cookies = SimpleCookie()
                cookies.load(cookie_string)
                self._cookies = {key: cookies[key].value for key in cookies}
            else:
                self._cookies = {}
        return self._cookies

    @property
    def body(self):
        if self._body is None:
            self._body = self.env['wsgi.input'].read()
        return self._body

    @property
    def ip(self):
        try:
            return self.env['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        except KeyError:
            return self.env['REMOTE_ADDR']

    @property
    def referer(self):
        return self.env.get('HTTP_REFERER')
