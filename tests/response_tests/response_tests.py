from tempfile import NamedTemporaryFile
from types import GeneratorType

from unittest import TestCase
from unittest.mock import Mock

from gatekeeper.responses.response import Response


class ResponseTestCase(TestCase):

    def test_default_values(self):
        response = Response()
        self.assertEqual(response.status, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/plain; charset=utf-8')
        self.assertEqual(response.body, b'')

    def test_wsgi(self):
        response = Response()
        response.status = 400
        response.headers['Content-Type'] = 'application/json'
        response.body = b'{"error": "Invalid token"}'
        start_respose = Mock()
        body = response.wsgi(start_respose)
        start_respose.assert_called_with('400 Bad Request', {'Content-Type': 'application/json'}.items())
        self.assertEqual(body, (b'{"error": "Invalid token"}',))

    def test_string_body_gets_converted_to_bytes(self):
        response = Response()
        response.body = 'hello world'
        self.assertEqual(response._wsgi_body(), (b'hello world',))

    def test_file_gets_returned_as_generator_to_wsgi(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'hello world')
            tmpfile.seek(0)
            response.file = tmpfile.name
            start_respose = Mock()
            self.assertIsInstance(response.wsgi(start_respose), GeneratorType)

    def test_all_file_contents_are_yielded_by_its_generator(self):
        response = Response()
        with NamedTemporaryFile() as tmpfile:
            tmpfile.write(b'hello world')
            tmpfile.seek(0)
            response.file = tmpfile.name
            start_respose = Mock()
            file_generator = response.wsgi(start_respose)
            contents = b''
            for chunk in file_generator:
                contents += chunk
            self.assertEqual(contents, b'hello world')
