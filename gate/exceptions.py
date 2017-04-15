class ResponseNotSet(Exception):

    def __init__(self):
        message = 'Accessing messages requires a response to be set'
        super(ResponseNotSet, self).__init__(message)


class UploadTargetAlreadyExists(Exception):

    def __init__(self):
        message = 'Upload target path already exists. Will not overwrite for security reasons.'
        super(UploadTargetAlreadyExists, self).__init__(message)


class DuplicateEndpoints(Exception):

    def __init__(self, path):
        message = 'Cannot register two endpoints with the same path: ' + path
        super(DuplicateEndpoints, self).__init__(message)


class AmbiguousEndpoints(Exception):

    def __init__(self, path):
        message = 'The same path is leading to different endpoints: ' + path
        super(AmbiguousEndpoints, self).__init__(message)


class JinjaEnvNotSet(Exception):

    def __init__(self):
        message = 'You need to set a Jinja environment before calling render'
        super(JinjaEnvNotSet, self).__init__(message)
