from .app_test_case import AppTestCase

from gatekeeper import App, Endpoint, HtmlEndpoint
from gatekeeper.exceptions import InvalidDirectory


class AppPagesTestCase(AppTestCase):

    def test_cannot_add_invalid_directory_for_pages(self):
        app = App()
        with self.assertRaises(InvalidDirectory):
            app.pages('tests/test_app/resources/pages1/index.html')

    def test_app_can_render_page(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '16'}
        expected_body = b'<h1> about </h1>'
        self.assert_call(app, 'GET', '/about', expected_status, expected_headers, expected_body)

    def test_app_can_render_a_page_even_if_it_ends_with_slash(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        self.assert_call(app, 'GET', '/about/', '200 OK')

    def test_app_can_render_index_page(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '16'}
        expected_body = b'<h1> index </h1>'
        self.assert_call(app, 'GET', '/', expected_status, expected_headers, expected_body)

    def test_app_can_render_index_page_on_subdirectory(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '19'}
        expected_body = b'<h1> settings </h1>'
        self.assert_call(app, 'GET', '/settings', expected_status, expected_headers, expected_body)

    def test_cannot_get_index_page_explicitly(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        self.assert_call(app, 'GET', '/index', '404 Not Found')
        self.assert_call(app, 'GET', '/settings/index', '404 Not Found')

    def test_can_render_pages_from_multiple_directories(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        app.pages('tests/test_app/resources/pages2')
        self.assert_call(app, 'GET', '/about', '200 OK')
        self.assert_call(app, 'GET', '/about2', '200 OK')

    def test_404_page_gets_rendered_if_status_matches_and_body_is_empty(self):
        app = App()
        app.pages('tests/test_app/resources/pages1')
        expected_status = '404 Not Found'
        expected_headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '18'}
        expected_body = b'<h1>Not Found</h1>'
        self.assert_call(app, 'GET', '/foobar', expected_status, expected_headers, expected_body)

    def test_status_page_works_even_if_status_is_200(self):
        class Hello(HtmlEndpoint):
            path = '/hello'
            def get(self, request, response):
                pass
        app = App()
        app.pages('tests/test_app/resources/pages1')
        app.endpoint(Hello)
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '11'}
        expected_body = b'<h1>OK</h1>'
        self.assert_call(app, 'GET', '/hello', expected_status, expected_headers, expected_body)

    def test_response_status_page_does_not_get_rendered_if_response_body_has_contents(self):
        class Hello(HtmlEndpoint):
            path = '/hello'
            def get(self, request, response):
                response.status = 404
                response.body = b'hello world'
        app = App()
        app.pages('tests/test_app/resources/pages1')
        app.endpoint(Hello)
        expected_status = '404 Not Found'
        expected_headers = {'Content-Type': 'text/html; charset=utf-8', 'Content-Length': '11'}
        expected_body = b'hello world'
        self.assert_call(app, 'GET', '/hello', expected_status, expected_headers, expected_body)

    def test_response_status_page_only_works_for_html_responses(self):
        class Hello(Endpoint):
            path = '/hello'
            def get(self, request, response):
                pass
        app = App()
        app.pages('tests/test_app/resources/pages1')
        app.endpoint(Hello)
        expected_status = '200 OK'
        expected_headers = {'Content-Type': 'text/plain; charset=utf-8', 'Content-Length': '0'}
        expected_body = b''
        self.assert_call(app, 'GET', '/hello', expected_status, expected_headers, expected_body)
