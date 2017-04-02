class Request(object):

    def __init__(self, env):
        self.env = env
        self._body = None

    @property
    def method(self):
        return self.env.get('REQUEST_METHOD')

    @property
    def url(self):
        url = self.scheme + '://' + self.host + self.path
        if self.query_string:
            url += '?' + self.query_string
        return url

    @property
    def scheme(self):
        return self.env.get('wsgi.url_scheme')

    @property
    def host(self):
        return self.env.get('HTTP_HOST')

    @property
    def path(self):
        return self.env.get('PATH_INFO')

    @property
    def query_string(self):
        return self.env.get('QUERY_STRING')

    @property
    def body(self):
        if self._body is None:
            self._body = self.env.get('wsgi.input').read()
        return self._body
