from .app_test_case import AppTestCase

from gatekeeper.app import App
from gatekeeper.endpoints.endpoint import Endpoint
from gatekeeper.exceptions import InvalidDirectory


class AppStaticTestCase(AppTestCase):

    def test_app_can_serve_static_content(self):
        app = App()
        app.static('tests/app_tests/static')
        expected_status = '200 OK'
        expected_headers = {
            'Content-Type': 'text/plain',
            'Content-Length': '26',
            'Content-Disposition': 'inline; filename="robots.txt"',
        }
        expected_body = b'User-agent: *\nDisallow: /\n'
        self.assert_call(app, 'GET', '/robots.txt', expected_status, expected_headers, expected_body)

    def test_app_can_serve_css_static_content_in_subdirectory(self):
        app = App()
        app.static('tests/app_tests/static')
        expected_status = '200 OK'
        expected_headers = {
            'Content-Type': 'text/css',
            'Content-Length': '32',
            'Content-Disposition': 'inline; filename="main.css"',
        }
        expected_body = b'body { margin: 0; padding: 0; }\n'
        self.assert_call(app, 'GET', '/css/main.css', expected_status, expected_headers, expected_body)

    def test_registered_static_path_may_end_in_slash_or_not(self):
        app = App()
        app.static('tests/app_tests/static')
        self.assert_call(app, 'GET', '/robots.txt', '200 OK')
        app = App()
        app.static('tests/app_tests/static/')
        self.assert_call(app, 'GET', '/robots.txt', '200 OK')

    def test_registering_static_content_fails_if_path_is_not_directory(self):
        app = App()
        with self.assertRaises(InvalidDirectory):
            app.static('tests/app_tests/static/robots.txt')

    def test_static_files_have_priority_over_endpoints(self):
        class Hello(Endpoint):
            path = '/robots.txt'
            def get(self, request, response):
                response.body = b'hello world'
        app = App()
        app.endpoint(Hello)
        app.static('tests/app_tests/static')
        self.assert_call(app, 'GET', '/robots.txt', None, None, b'User-agent: *\nDisallow: /\n')

    def test_app_can_serve_static_content_from_multiple_directories(self):
        app = App()
        app.static('tests/app_tests/static')
        app.static('tests/app_tests/static2')
        self.assert_call(app, 'GET', '/robots.txt', '200 OK')
        self.assert_call(app, 'GET', '/readme.txt', '200 OK')
