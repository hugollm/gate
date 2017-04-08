from .response import Response


class JsonResponse(Response):

    def __init__(self):
        super(JsonResponse, self).__init__()
        self.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.body = b'null'
        self.json = {}
