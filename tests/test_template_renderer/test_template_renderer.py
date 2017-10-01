from unittest import TestCase
from jinja2.exceptions import TemplateNotFound
from gatekeeper.template_renderer import TemplateRenderer


class TemplateRendererTestCase(TestCase):

    def test_can_render_template_from_directory(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        text = renderer.render('simple.html')
        self.assertEqual(text, '<h1>Simple</h1>')

    def test_can_render_template_with_context(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        text = renderer.render('with_context.html', {'name': 'John'})
        self.assertEqual(text, '<h1>Hello John</h1>')

    def test_escape(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        text = renderer.render('with_special_chars.html', {'name': 'John'})
        self.assertEqual(text, '&lt;h1&gt;Hello World&lt;/h1&gt;')

    def test_can_render_child_template_from_subdirectory(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        text = renderer.render('subdirectory/simple.html')
        self.assertEqual(text, '<h1>Simple</h1>')

    def test_can_render_templates_from_different_directories(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        renderer.add_directory('tests/test_template_renderer/resources/templates2')
        text1 = renderer.render('simple.html')
        text2 = renderer.render('simple2.html')
        self.assertEqual(text1, '<h1>Simple</h1>')
        self.assertEqual(text2, '<h1>Templates2/Simple2</h1>')

    def test_directories_added_first_have_priority(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates2')
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        text = renderer.render('simple.html')
        self.assertEqual(text, '<h1>Templates2/Simple</h1>')

    def test_jinja_env_is_constructed_only_once_after_first_render(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/test_template_renderer/resources/templates1')
        renderer.render('simple.html')
        renderer.add_directory('tests/test_template_renderer/resources/templates2')
        with self.assertRaises(TemplateNotFound):
            renderer.render('simple2.html')

    def test_can_render_template_from_package(self):
        renderer = TemplateRenderer()
        renderer.add_package('tests.test_template_renderer.resources.package1')
        text = renderer.render('tests.test_template_renderer.resources.package1/simple.html')
        self.assertEqual(text, '<h1>Simple</h1>')

    def test_can_render_templates_from_different_packages(self):
        renderer = TemplateRenderer()
        renderer.add_package('tests.test_template_renderer.resources.package1')
        renderer.add_package('tests.test_template_renderer.resources.package2')
        text1 = renderer.render('tests.test_template_renderer.resources.package1/simple.html')
        text2 = renderer.render('tests.test_template_renderer.resources.package2/simple.html')
        self.assertEqual(text1, '<h1>Simple</h1>')
        self.assertEqual(text2, '<h1>Simple</h1>')
