from importlib import import_module
from unittest.mock import patch

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

    def test_registering_empty_package_does_not_register_any_endpoint(self):
        app = App()
        app.package('tests.test_app.resources.empty_package')
        self.assertEqual(app.endpoints, [])

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

    def test_registered_package_is_scanned_using_real_directory_path(self):
        app = App()
        with patch('gatekeeper.app.walk_packages') as mock:
            app.package('tests.test_app.resources.empty_package')
        package = import_module('tests.test_app.resources.empty_package')
        mock.assert_called_once_with(package.__path__)
