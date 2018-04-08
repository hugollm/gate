from datetime import datetime, date, time
from decimal import Decimal
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
            self._body = json.dumps(self.json, cls=CustomJsonEncoder).encode('utf-8')
        return self._body

    def wsgi(self, start_respose):
        self.freeze = True
        return super(JsonResponse, self).wsgi(start_respose)


class CustomJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime) or isinstance(obj, date) or isinstance(obj, time):
            return obj.isoformat()
        return super(CustomJsonEncoder, self).default(obj)
