from ..package1.endpoints.hello import Hello


class HelloInherited(Hello):

    def get(self, request, response):
        response.body = b'hello inherited'
