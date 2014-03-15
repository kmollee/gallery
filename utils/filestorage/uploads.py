import os
import uuid


def get_unique_upload_path(instance, filename):
    """
    Gets the upload path for a file. Folder is based on the app_label.
    File name with path is guaranteed to be unique by using a UUID.
    An example path for an image in the "photos" application looks like this:
        photos/bc31d8ba49c149598f83cf6c64eed500.jpg
    """
    filename, extension = os.path.splitext(filename)
    new_filename = "%s%s" % (
        str(uuid.uuid4()).replace("-", ""), extension.lower())
    return os.path.join(instance._meta.app_label.lower(), new_filename)
