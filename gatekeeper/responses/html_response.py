from .response import Response
from ..exceptions import JinjaEnvNotSet


class HtmlResponse(Response):

    def __init__(self):
        super(HtmlResponse, self).__init__()
        self.headers['Content-Type'] = 'text/html; charset=utf-8'
        self.jinja_env = None
        self.context = {}

    def render(self, template_identifier, context):
        from jinja2 import Template
        if self.jinja_env is None:
            raise JinjaEnvNotSet()
        template = self.jinja_env.get_template(template_identifier)
        context = context or {}
        context.pop('self', None)
        self.context = context
        self.body = template.render(**context)
