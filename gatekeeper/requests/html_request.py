from io import BytesIO
import os.path
import cgi
from warnings import warn

from .request import Request


class HtmlRequest(Request):

    def __init__(self, env):
        super(HtmlRequest, self).__init__(env)
        self._form = None
        self._files = None
        self._cgi_form = None

    @property
    def form(self):
        if self._form is None:
            self._form = {}
            for key in self.cgi_form:
                item = self.cgi_form[key]
                if not self._cgi_item_is_file(item):
                    self._form[key] = self.cgi_form.getvalue(key)
        return self._form

    @property
    def files(self):
        if self._files is None:
            self._files = {}
            for key in self.cgi_form:
                item = self.cgi_form[key]
                if self._cgi_item_is_file(item):
                    self._files[key] = self._get_uploaded_file_from_cgi_item(item)
            if not self._files:
                warn('Trying to get files from request but there\'s none. Are you missing enctype="multipart/form-data" in your form tag?')
        return self._files

    @property
    def cgi_form(self):
        if self._cgi_form is None:
            self._cgi_form = cgi.FieldStorage(fp=BytesIO(self.body), environ=self.env)
        return self._cgi_form

    def _cgi_item_is_file(self, item):
        test_subject = item[0] if isinstance(item, list) else item
        return bool(getattr(test_subject, 'filename', None))

    def _get_uploaded_file_from_cgi_item(self, item):
        if isinstance(item, list):
            files = []
            for value in item:
                files.append(UploadedFile(value))
            return files
        else:
            return UploadedFile(item)


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


class UploadTargetAlreadyExists(Exception):

    def __init__(self):
        message = 'Upload target path already exists. Will not overwrite for security reasons.'
        super(UploadTargetAlreadyExists, self).__init__(message)
