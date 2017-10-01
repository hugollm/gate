from gatekeeper import Endpoint


class Hello(Endpoint):

    path = '/hello'

    def get(self, request, response):
        response.body = 'hello world'
