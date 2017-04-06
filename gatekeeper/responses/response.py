from http.client import responses as STATUS_MESSAGES


class Response(object):

    def __init__(self):
        self.status = 200
        self.headers = {'Content-Type': 'text/plain; charset=utf-8'}
        self.body = b''
        self.file = None

    def wsgi(self, start_respose):
        start_respose(self._wsgi_status(), self._wsgi_headers())
        if self.file:
            return self._wsgi_file()
        return self._wsgi_body()

    def _wsgi_status(self):
        return str(self.status) + ' ' + STATUS_MESSAGES.get(self.status, '')

    def _wsgi_headers(self):
        return self.headers.items()

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
