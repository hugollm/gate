from unittest import TestCase

from gatekeeper.app import App
from gatekeeper.test_client import TestClient
from gatekeeper.endpoints.endpoint import Endpoint
from gatekeeper.endpoints.html_endpoint import HtmlEndpoint
from gatekeeper.endpoints.json_endpoint import JsonEndpoint


class TestClientTestCase(TestCase):

    def setUp(self):
        self.app = App()
        self.client = TestClient(self.app)

    def test_get_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.get('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_post_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def post(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_put_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def put(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.put('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_patch_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def patch(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.patch('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_delete_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def delete(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.delete('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_head_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def head(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.head('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_options_request(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def options(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.options('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_query_argument(self):
        class HelloWorld(Endpoint):
            endpoint_path = '/hello'
            def get(self, request, response):
                response.body = 'page: ' + request.query['page']
        self.app.endpoint(HelloWorld)
        response = self.client.get('/hello', query={'page': 1})
        self.assertEqual(response.body, 'page: 1')

    def test_form_argument(self):
        class HelloWorld(HtmlEndpoint):
            endpoint_path = '/hello'
            def post(self, request, response):
                response.body = 'name: ' + request.form['name']
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello', form={'name': 'john'})
        self.assertEqual(response.body, 'name: john')

    def test_json_argument(self):
        class HelloWorld(JsonEndpoint):
            endpoint_path = '/hello'
            def post(self, request, response):
                response.json = request.json
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello', json={'name': 'jane'})
        self.assertEqual(response.body, '{"name": "jane"}')
