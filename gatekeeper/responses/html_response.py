from .response import Response


class HtmlResponse(Response):

    def __init__(self):
        super(HtmlResponse, self).__init__()
        self.headers['Content-Type'] = 'text/html; charset=utf-8'
