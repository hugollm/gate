import json
from .response import Response


class JsonResponse(Response):

    def __init__(self):
        super(JsonResponse, self).__init__()
        self.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.json = {}
        self.freeze = False

    @property
    def body(self):
        if not self.freeze:
            self._body = json.dumps(self.json).encode('utf-8')
        return self._body

    def wsgi(self, start_respose):
        self.freeze = True
        return super(JsonResponse, self).wsgi(start_respose)
