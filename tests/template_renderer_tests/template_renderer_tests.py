from unittest import TestCase
from jinja2.exceptions import TemplateNotFound
from gatekeeper.template_renderer import TemplateRenderer


class TemplateRendererTestCase(TestCase):

    def test_can_render_template_from_directory(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site')
        text = renderer.render('base.html')
        self.assertEqual(text, '<body></body>')

    def test_can_render_template_with_context(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site')
        text = renderer.render('hello.html', {'name': 'John'})
        self.assertEqual(text, '<h1>Hello John</h1>')

    def test_escape(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site')
        text = renderer.render('markup.html', {'name': 'John'})
        self.assertEqual(text, '&lt;h1&gt;Hello World&lt;/h1&gt;')

    def test_can_render_child_template_from_subdirectory(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site')
        text = renderer.render('pages/index.html')
        self.assertEqual(text, '<body> index site1 </body>')

    def test_can_render_templates_from_different_directories(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site')
        renderer.add_directory('tests/template_renderer_tests/site2')
        text1 = renderer.render('pages/index.html')
        text2 = renderer.render('index.html')
        self.assertEqual(text1, '<body> index site1 </body>')
        self.assertEqual(text2, 'index site2')

    def test_directories_added_first_have_priority(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site2')
        renderer.add_directory('tests/template_renderer_tests/site')
        text = renderer.render('base.html')
        self.assertEqual(text, '<h1></h1>')

    def test_jinja_env_is_constructed_only_once_after_first_render(self):
        renderer = TemplateRenderer()
        renderer.add_directory('tests/template_renderer_tests/site')
        renderer.render('base.html')
        renderer.add_directory('tests/template_renderer_tests/site2')
        with self.assertRaises(TemplateNotFound):
            renderer.render('index.html')

    def test_can_render_template_from_package(self):
        renderer = TemplateRenderer()
        renderer.add_package('tests.template_renderer_tests.base')
        text = renderer.render('tests.template_renderer_tests.base/base.html')
        self.assertEqual(text, '<body></body>')

    def test_can_render_templates_from_different_packages(self):
        renderer = TemplateRenderer()
        renderer.add_package('tests.template_renderer_tests.base')
        renderer.add_package('tests.template_renderer_tests.hello')
        text = renderer.render('tests.template_renderer_tests.hello/hello.html', {'name': 'John'})
        self.assertEqual(text, '<body><h1>Hello John</h1></body>')
