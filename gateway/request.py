import cgi
from urllib.parse import parse_qsl
from .request_file import RequestFile


class Request(object):

    def __init__(self, env):
        self.env = env
        self._body = None
        self._query = None
        self._form = None
        self._files = None
        self._cgi_form = None

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
    def body(self):
        if self._body is None:
            self._body = self.env['wsgi.input'].read()
        return self._body

    @property
    def query(self):
        if self._query is None:
            self._query = dict(parse_qsl(self.query_string, keep_blank_values=True))
        return self._query

    @property
    def form(self):
        if self._form is None:
            self._form = {}
            for key in self.cgi_form:
                item = self.cgi_form[key]
                if not self._cgi_item_is_file(item):
                    self._form[key] = self.cgi_form.getvalue(key)
        return self._form

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for key in self.cgi_form:
                item = self.cgi_form[key]
                if self._cgi_item_is_file(item):
                    self._files[key] = self._get_request_file_from_cgi_item(item)
        return self._files

    @property
    def cgi_form(self):
        if self._cgi_form is None:
            self._cgi_form = cgi.FieldStorage(fp=self.env['wsgi.input'], environ=self.env)
        return self._cgi_form

    def _cgi_item_is_file(self, item):
        test_subject = item[0] if isinstance(item, list) else item
        return bool(getattr(test_subject, 'filename', None))

    def _get_request_file_from_cgi_item(self, item):
        if isinstance(item, list):
            files = []
            for value in item:
                files.append(RequestFile(value))
            return files
        else:
            return RequestFile(item)
