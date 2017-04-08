from gatekeeper.endpoints.endpoint import Endpoint


class SimpleGet(Endpoint):

    endpoint_path = '/'

    def get(self, request, response):
        response.body = b'hello world'
