from .app_test_case import AppTestCase
from gatekeeper import App


class AppPackageTestCase(AppTestCase):

    def test_cannot_register_invalid_package_path(self):
        app = App()
        with self.assertRaises(ImportError):
            app.package('tests.test_app.resources.invalid')

    def test_can_render_template_from_app_package(self):
        app = App()
        app.package('tests.test_app.resources.package1')
        text = app.template_renderer.render('tests.test_app.resources.package1/simple.html')
        self.assertEqual(text, '<h1>Simple</h1>')

    def test_can_reach_endpoint_on_registered_package(self):
        app = App()
        app.package('tests.test_app.resources.package1')
        self.assert_call(app, 'GET', '/hello', '200 OK')

    def test_app_can_register_empty_package(self):
        app = App()
        app.package('tests.test_app.resources.empty_package')

    def test_app_can_reach_endpoints_from_multiple_packages(self):
        app = App()
        app.package('tests.test_app.resources.package1')
        app.package('tests.test_app.resources.package2')
        app.package('tests.test_app.resources.empty_package')
        self.assert_call(app, 'GET', '/hello', '200 OK')
        self.assert_call(app, 'GET', '/hello2', '200 OK')

    def test_imported_endpoints_used_for_inheritance_dont_get_mistakenly_registered(self):
        app = App()
        app.package('tests.test_app.resources.package3')
        from .resources.package1.endpoints.hello import Hello
        for endpoint in app.endpoints:
            self.assertIsNot(endpoint.__class__, Hello)
