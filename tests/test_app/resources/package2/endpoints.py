from gatekeeper import JsonEndpoint


class Hello2(JsonEndpoint):

    path = '/hello2'

    def get(self, request, response):
        response.json = {'hello': 'world'}
