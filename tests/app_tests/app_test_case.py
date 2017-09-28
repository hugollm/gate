from unittest import TestCase
from unittest.mock import Mock


class AppTestCase(TestCase):

    def assert_call(self, app, method, path, expected_status=None, expected_headers=None, expected_body=None):
        env = {'REQUEST_METHOD': method, 'PATH_INFO': path}
        start_response = Mock()
        body = b''.join(app(env, start_response))
        status = start_response.call_args[0][0]
        headers = start_response.call_args[0][1]
        if expected_status is not None:
            self.assertEqual(status, expected_status)
        if expected_headers is not None:
            expected_headers = sorted(expected_headers.items())
            headers = sorted(headers)
            self.assertEqual(headers, expected_headers)
        if expected_body is not None:
            self.assertEqual(body, expected_body)
