class UploadTargetPathAlreadyExists(Exception):

    def __init__(self):
        message = 'Upload target path already exists. Will not overwrite for security reasons.'
        super(UploadTargetPathAlreadyExists, self).__init__(message)
