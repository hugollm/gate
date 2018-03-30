from .response import Response


class HtmlResponse(Response):

    def __init__(self):
        super(HtmlResponse, self).__init__()
        self.headers['Content-Type'] = 'text/html; charset=utf-8'

    def set_message(self, key, value):
        self.set_cookie('MESSAGE:' + key, value, http_only=False, same_site=False)

    def unset_message(self, key):
        self.unset_cookie('MESSAGE:' + key)
