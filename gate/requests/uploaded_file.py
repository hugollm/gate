import os.path
from ..exceptions import UploadTargetAlreadyExists


class UploadedFile(object):

    name = None
    stream = None
    encoding = None
    type = None

    def __init__(self, cgi_field):
        self.name = cgi_field.filename
        self.stream = cgi_field.file
        self.encoding = cgi_field.encoding
        self.type = cgi_field.type

    def save(self, path):
        if os.path.exists(path):
            raise UploadTargetAlreadyExists()
        with open(path, 'wb') as file:
            self.stream.seek(0)
            while True:
                chunk = self.stream.read(1024)
                if not chunk:
                    break;
                file.write(chunk)
