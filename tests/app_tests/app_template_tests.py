from .app_test_case import AppTestCase

from jinja2 import Environment

from gatekeeper.app import App
from gatekeeper.endpoints.endpoint import Endpoint
from gatekeeper.endpoints.html_endpoint import HtmlEndpoint
from gatekeeper.exceptions import JinjaEnvNotSet


class AppTemplateTestCase(AppTestCase):

    def test_set_jinja_env(self):
        app = App()
        app.set_jinja_env({'tests.app_tests.hello': 'templates'})
        self.assertIsInstance(app.jinja_env, Environment)

    def test_render(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        text = app.render('tests.app_tests.hello/hello.html', {'name': 'John'})
        self.assertEqual(text, '<body><h1>Hello John</h1></body>')

    def test_render_can_be_called_without_context(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        text = app.render('tests.app_tests.hello/hello.html')
        self.assertEqual(text, '<body><h1>Hello </h1></body>')

    def test_render_can_be_called_with_locals_as_context(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        name = 'John'
        text = app.render('tests.app_tests.hello/hello.html', locals())
        self.assertEqual(text, '<body><h1>Hello John</h1></body>')

    def test_calling_render_without_setting_jinja_env_raises_exception(self):
        app = App()
        with self.assertRaises(JinjaEnvNotSet):
            app.render('tests.app_tests.hello/hello.html')

    def test_html_responses_can_render_if_jinja_env_is_set_on_app(self):
        class Hello(HtmlEndpoint):
            path = '/'
            def get(self, request, response):
                name = 'John'
                response.render('tests.app_tests.hello/hello.html', locals())
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        app.endpoint(Hello)
        expected_body = b'<body><h1>Hello John</h1></body>'
        self.assert_call(app, 'GET', '/', expected_body=expected_body)

    def test_html_responses_have_a_context_set_after_rendering(self):
        class Hello(HtmlEndpoint):
            path = '/'
            def get(self, request, response):
                name = 'John'
                response.render('tests.app_tests.hello/hello.html', locals())
                assert response.context == {'request': request, 'response': response, 'name': 'John'}
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        app.endpoint(Hello)
        self.assert_call(app, 'GET', '/', '200 OK')

    def test_html_responses_cannot_render_if_jinja_env_is_not_set_on_app(self):
        class Hello(HtmlEndpoint):
            path = '/'
            def get(self, request, response):
                name = 'John'
                response.render('tests.app_tests.hello/hello.html', locals())
        app = App()
        app.endpoint(Hello)
        with self.assertRaises(JinjaEnvNotSet):
            self.assert_call(app, 'GET', '/')

    def test_html_endpoints_and_responses_that_are_html_dont_get_jinja_env_from_app(self):
        class WithJinjaEnv(HtmlEndpoint):
            path = '/'
            def get(self, request, response):
                assert self.jinja_env is not None
                assert response.jinja_env is not None
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        app.endpoint(WithJinjaEnv)
        self.assert_call(app, 'GET', '/', '200 OK')

    def test_endpoints_and_responses_that_are_not_html_dont_get_jinja_env_from_app(self):
        class NoJinjaEnv(Endpoint):
            path = '/'
            def get(self, request, response):
                assert getattr(self, 'jinja_env', None) is None
                assert getattr(response, 'jinja_env', None) is None
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        app.endpoint(NoJinjaEnv)
        self.assert_call(app, 'GET', '/', '200 OK')

    def test_templates_are_in_autoescape_mode_by_default(self):
        app = App()
        app.set_jinja_env({
            'tests.app_tests.base': 'base_templates',
            'tests.app_tests.hello': 'hello_templates',
        })
        text = app.render('tests.app_tests.hello/markup.html', {'name': 'John'})
        self.assertEqual(text, '<body>&lt;h1&gt;Hello World&lt;/h1&gt;</body>')
