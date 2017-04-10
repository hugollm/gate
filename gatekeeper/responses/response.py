from http.client import responses as STATUS_MESSAGES
from http.cookies import SimpleCookie


class Response(BaseException):

    def __init__(self):
        self.status = 200
        self.headers = {'Content-Type': 'text/plain; charset=utf-8'}
        self.cookies = []
        self.body = b''
        self.file = None

    def redirect(self, uri):
        self.status = 303
        self.headers['Location'] = uri
        return self

    def not_found(self):
        self.status = 404
        return self

    def bad_request(self):
        self.status = 400
        return self

    def unauthorized(self):
        self.status = 401
        return self

    def forbidden(self):
        self.status = 403
        return self

    def set_cookie(self, key, value, expires=None, domain=None, path=None, secure=False, http_only=True, same_site=True):
        cookie = SimpleCookie({key: value}).get(key).OutputString()
        if expires:
            cookie += '; Expires=' + expires.strftime('%a, %d %b %Y %T') + ' GMT'
        if domain:
            cookie += '; Domain=' + domain
        if path:
            cookie += '; Path=' + path
        if secure:
            cookie += '; Secure'
        if http_only:
            cookie += '; HttpOnly'
        if same_site:
            cookie += '; SameSite=Strict'
        self.cookies.append(cookie)

    def wsgi(self, start_respose):
        start_respose(self._wsgi_status(), self._wsgi_headers())
        if self.file:
            return self._wsgi_file()
        return self._wsgi_body()

    def _wsgi_status(self):
        return str(self.status) + ' ' + STATUS_MESSAGES.get(self.status, '')

    def _wsgi_headers(self):
        headers = list(self.headers.items())
        for cookie in self.cookies:
            headers.append(('Set-Cookie', cookie))
        return headers

    def _wsgi_body(self):
        if type(self.body) is not bytes:
            self.body = self.body.encode('utf-8')
        return (self.body,)

    def _wsgi_file(self):
        with open(self.file, 'rb') as f:
            mbyte = 1024 ** 2
            while True:
                chunk = f.read(mbyte)
                if not chunk:
                    break
                yield chunk
