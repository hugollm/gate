class TemplateRenderer(object):

    def __init__(self):
        self.directories = []
        self.packages = []
        self.jinja_env = None

    def add_directory(self, path):
        self.directories.append(path)

    def add_package(self, package):
        self.packages.append(package)

    def render(self, template_identifier, context=None):
        self._set_env_once()
        template = self.jinja_env.get_template(template_identifier)
        context = context or {}
        context.pop('self', None)
        return template.render(**context)

    def _set_env_once(self):
        if self.jinja_env:
            return
        from jinja2 import Environment, select_autoescape
        loader = self._make_loader()
        autoescape = select_autoescape(default=True, default_for_string=True)
        self.jinja_env = Environment(loader=loader, autoescape=autoescape)

    def _make_loader(self):
        from jinja2 import ChoiceLoader, FileSystemLoader
        directory_loader = FileSystemLoader(self.directories)
        package_loader = self._make_package_loader()
        return ChoiceLoader([directory_loader, package_loader])

    def _make_package_loader(self):
        from jinja2 import PrefixLoader, PackageLoader
        prefix_map = {}
        for package in self.packages:
            prefix_map[package] = PackageLoader(package, 'templates')
        return PrefixLoader(prefix_map)
