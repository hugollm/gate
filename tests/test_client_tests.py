from tempfile import NamedTemporaryFile
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
            path = '/hello'
            def get(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.get('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_post_request(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def post(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_put_request(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def put(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.put('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_patch_request(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def patch(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.patch('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_delete_request(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def delete(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.delete('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_head_request(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def head(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.head('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_options_request(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def options(self, request, response):
                response.body = b'hello world'
        self.app.endpoint(HelloWorld)
        response = self.client.options('/hello')
        self.assertEqual(response.body, b'hello world')

    def test_query_argument(self):
        class HelloWorld(Endpoint):
            path = '/hello'
            def get(self, request, response):
                response.body = 'page: ' + request.query['page']
        self.app.endpoint(HelloWorld)
        response = self.client.get('/hello', query={'page': 1})
        self.assertEqual(response.body, 'page: 1')

    def test_form_argument(self):
        class HelloWorld(HtmlEndpoint):
            path = '/hello'
            def post(self, request, response):
                response.body = 'name: ' + request.form['name']
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello', form={'name': 'john'})
        self.assertEqual(response.body, 'name: john')

    def test_form_argument_with_list_as_value(self):
        class HelloWorld(HtmlEndpoint):
            path = '/hello'
            def post(self, request, response):
                assert request.form['names'] == ['john', 'jane']
                response.body = 'name: ' + ', '.join(request.form['names'])
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello', form={'names': ['john', 'jane']})
        self.assertEqual(response.body, 'name: john, jane')

    def test_form_argument_with_list_of_numbers(self):
        class HelloWorld(HtmlEndpoint):
            path = '/hello'
            def post(self, request, response):
                assert request.form['user_ids'] == ['1', '2', '3']
                response.body = 'ids: ' + ', '.join(request.form['user_ids'])
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello', form={'user_ids': [1, 2, 3]})
        self.assertEqual(response.body, 'ids: 1, 2, 3')

    def test_json_argument(self):
        class HelloWorld(JsonEndpoint):
            path = '/hello'
            def post(self, request, response):
                response.json = request.json
        self.app.endpoint(HelloWorld)
        response = self.client.post('/hello', json={'name': 'jane'})
        self.assertEqual(response.body, '{"name": "jane"}')

    def test_client_keeps_cookies_and_sends_them_in_subsequent_requests(self):
        class Login(HtmlEndpoint):
            path = '/login'
            def get(self, request, response):
                response.body = request.cookies.get('token')
            def post(self, request, response):
                response.set_cookie('token', 'abc')
        self.app.endpoint(Login)
        self.client.post('/login')
        response = self.client.get('/login')
        self.assertEqual(response.body, 'abc')

    def test_client_can_handle_cookies_with_special_characters(self):
        class Login(HtmlEndpoint):
            path = '/login'
            def get(self, request, response):
                response.body = request.cookies.get('token')
            def post(self, request, response):
                response.set_cookie('token', 'abc/;,~áç[\'!""]')
        self.app.endpoint(Login)
        self.client.post('/login')
        response = self.client.get('/login')
        self.assertEqual(response.body, 'abc/;,~áç[\'!""]')

    def test_client_can_handle_two_cookies_at_once_and_one_with_special_characters(self):
        class Login(HtmlEndpoint):
            path = '/login'
            def get(self, request, response):
                response.body = request.cookies.get('token1') + '|' + request.cookies.get('token2')
            def post(self, request, response):
                response.set_cookie('token1', 'abc')
                response.set_cookie('token2', 'abc/;,~áç[\'!""]')
        self.app.endpoint(Login)
        self.client.post('/login')
        response = self.client.get('/login')
        self.assertEqual(response.body, 'abc|abc/;,~áç[\'!""]')

    def test_client_can_unset_cookie(self):
        class Login(HtmlEndpoint):
            path = '/login'
            def post(self, request, response):
                response.set_cookie('session-id', 'abc')
        class Logout(HtmlEndpoint):
            path = '/logout'
            def post(self, request, response):
                response.unset_cookie('session-id')
        class Dashboard(HtmlEndpoint):
            path = '/dashboard'
            def get(self, request, response):
                assert 'session-id' not in request.cookies
        self.app.endpoint(Login)
        self.app.endpoint(Logout)
        self.app.endpoint(Dashboard)
        self.client.post('/login')
        self.client.post('/logout')
        self.client.get('/dashboard')

    def test_client_can_upload_file_with_post(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def post(self, request, response):
                photo = request.files['photo']
                assert photo.stream.read() == b'IMAGE CONTENT'
        self.app.endpoint(Upload)
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'IMAGE CONTENT')
            tmpfile.seek(0)
            response = self.client.post('/upload', files={'photo': tmpfile.name})
            self.assertEqual(response.status, 200)

    def test_client_can_upload_file_with_put(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def put(self, request, response):
                photo = request.files['photo']
                assert photo.stream.read() == b'IMAGE CONTENT'
        self.app.endpoint(Upload)
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'IMAGE CONTENT')
            tmpfile.seek(0)
            response = self.client.put('/upload', files={'photo': tmpfile.name})
            self.assertEqual(response.status, 200)

    def test_client_can_upload_file_with_patch(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def patch(self, request, response):
                photo = request.files['photo']
                assert photo.stream.read() == b'IMAGE CONTENT'
        self.app.endpoint(Upload)
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'IMAGE CONTENT')
            tmpfile.seek(0)
            response = self.client.patch('/upload', files={'photo': tmpfile.name})
            self.assertEqual(response.status, 200)

    def test_client_can_upload_two_files(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def post(self, request, response):
                photo1 = request.files['photo1']
                photo2 = request.files['photo2']
                assert photo1.stream.read() == b'IMAGE CONTENT 1'
                assert photo2.stream.read() == b'IMAGE CONTENT 2'
        self.app.endpoint(Upload)
        with NamedTemporaryFile() as tmpfile1:
            with NamedTemporaryFile() as tmpfile2:
                tmpfile1.write(b'IMAGE CONTENT 1')
                tmpfile2.write(b'IMAGE CONTENT 2')
                tmpfile1.seek(0)
                tmpfile2.seek(0)
                response = self.client.post('/upload', files={'photo1': tmpfile1.name, 'photo2': tmpfile2.name})
                self.assertEqual(response.status, 200)

    def test_client_can_upload_two_files_along_with_form_content(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def post(self, request, response):
                assert request.form == {'name': 'john', 'age': '23'}
                photo1 = request.files['photo1']
                photo2 = request.files['photo2']
                assert photo1.stream.read() == b'IMAGE CONTENT 1'
                assert photo2.stream.read() == b'IMAGE CONTENT 2'
        self.app.endpoint(Upload)
        with NamedTemporaryFile() as tmpfile1:
            with NamedTemporaryFile() as tmpfile2:
                tmpfile1.write(b'IMAGE CONTENT 1')
                tmpfile2.write(b'IMAGE CONTENT 2')
                tmpfile1.seek(0)
                tmpfile2.seek(0)
                form = {'name': 'john', 'age': 23}
                response = self.client.post('/upload', form=form, files={
                    'photo1': tmpfile1.name,
                    'photo2': tmpfile2.name,
                })
                self.assertEqual(response.status, 200)

    def test_uploaded_file_with_client_gets_name_and_type_right(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def post(self, request, response):
                photo = request.files['photo']
                assert photo.name.endswith('.png')
                assert photo.type == 'image/png'
        self.app.endpoint(Upload)
        with NamedTemporaryFile(suffix='.png') as tmpfile:
            response = self.client.post('/upload', files={'photo': tmpfile.name})
            self.assertEqual(response.status, 200)

    def test_client_sets_uploaded_file_mime_type_as_octet_stream_if_it_cant_guess_it(self):
        class Upload(HtmlEndpoint):
            path = '/upload'
            def post(self, request, response):
                photo = request.files['photo']
                assert photo.type == 'application/octet-stream'
        self.app.endpoint(Upload)
        with NamedTemporaryFile() as tmpfile:
            response = self.client.post('/upload', files={'photo': tmpfile.name})
            self.assertEqual(response.status, 200)
