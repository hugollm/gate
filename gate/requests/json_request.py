import json
from .request import Request


class JsonRequest(Request):

    def __init__(self, env):
        super(JsonRequest, self).__init__(env)
        self._json = None
        self._json_loaded = False

    @property
    def json(self):
        if not self._json_loaded:
            self._json = json.loads(self.body.decode('utf-8'))
            self._json_loaded = True
        return self._json
