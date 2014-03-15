import re
import os

from PIL import Image as PILImage, ImageOps as PILImageOps
from PIL.ExifTags import TAGS as PIL_TAGS

from django.conf import settings


def split_extension(filename):
    """
    Given a filename, splits out the extension and returns just the filename
    and then just the extension.
    Examples:
    'awesome_filename.jpg' => ['awesome_filename', 'jpg']
    'path/awesome_filename.jpg' => ['path/awesome_filename', 'jpg']
    """
    fname, ext = os.path.splitext(filename)
    if ext.startswith('.'):
        ext = ext[1:]
    return fname, ext.lower()


def friendly_filename(filename):
    """
    Creates a 'friendly' filename based on the given filename. The
    transformation process is as follows:
    - Get everything after the last slash
    - Remove the extension
    - Convert slashes, underscores, bracket, pound to space
    - Convert consecutive spaces to just one space
    Examples:
    'awesome_filename.jpg' => 'awesome filename'
    'path/here/awesome_filename.jpg' => 'awesome filename'
    'my photo #  03.jpg' => 'my photo 03'
    'messy__photo name  [3] 04.jpg' => 'messy photo name 3 04'
    """
    # get everything after the last slash
    filename = filename.split('\\')[-1].split('/')[-1]
    # remove extension
    filename, ext = split_extension(filename)
    # convert slashes\underscores\bracket\pound to space
    filename = re.sub('[/\\_\[\]#]', ' ', filename)
    # convert two or more spaces to just one space
    filename = re.sub('\s{2,}', ' ', filename)
    return filename.strip()[:200]


def file_allowed(filename):
    """
    Determines whether the given filename is allowed to be uploaded. This is
    based on the extension and the ALLOWED_EXTENSIONS setting.
    """
    filename, ext = split_extension(filename)
    return (ext in settings.ALLOWED_EXTENSIONS)


def parse_size(size):
    """
    Converts a size specified as '800x600-fit' to a list like [800, 600]
    and a string 'fit'. The strings in the error messages are really for the
    developer so they don't need to be translated.
    """
    first_split = size.split('-')
    if len(first_split) != 2:
        raise AttributeError(
            'Size must be specified as 000x000-method such as 800x600-fit.')
    size, method = first_split
    if method not in ('fit', 'thumb'):
        raise AttributeError(
            'The method must either be "fit" or "thumb", not "%s".' % method)
    try:
        size_ints = [int(x) for x in size.split('x')]
    except ValueError:
        raise AttributeError(
            'Size must be specified as 000x000-method such as 800x600-fit.')
    if len(size_ints) != 2:
        raise AttributeError(
            'Size must be specified as 000x000-method such as 800x600-fit.')
    if size_ints[0] <= 0 or size_ints[1] <= 0:
        raise AttributeError(
            'Height and width for size must both be greater than 0.')
    return size_ints, method


def get_thumbnail_path(filename, key):
    """
    Gets the upload path for a thumbnail file.
    An example path for an image in the 'photos' application looks like this:
        photos/bc31d8ba49c149598f83cf6c64eed500.jpg
        photos/thumbnails/bc31d8ba49c149598f83cf6c64eed500-800x600-thumb.jpg
        photos/thumbnails/bc31d8ba49c149598f83cf6c64eed500-200x150-fit.jpg
    """
    filename, extension = os.path.splitext(filename)
    path, filename = os.path.split(filename)
    new_filename = '%s-%s%s' % (filename, key, extension)
    # Create the full thumbnail path if necessary.
    os.makedirs(os.path.join(
        settings.MEDIA_ROOT, path, 'thumbnails'), 0o775, exist_ok=True)
    return os.path.join(path, 'thumbnails', new_filename)


def generate_thumbnail(image_field, size):
    """
    Generate a thumbnail image for the given image_field. Size is required and
    should be passed as a string like '800x600-fit'. The file is always
    generated regardless of whether it exists. This function will use the
    same storage as the image_field that is passed in.
    """
    size_ints, method = parse_size(size)
    thumbnail_path = get_thumbnail_path(image_field.name, size)
    pimage = PILImage.open(image_field.path)
    if method == 'fit':
        pimage = PILImageOps.fit(
            pimage,
            size_ints,
            method=PILImage.ANTIALIAS)
    elif method == 'thumb':
        pimage.thumbnail(size_ints, PILImage.ANTIALIAS)
    pimage.save(image_field.storage.path(thumbnail_path))
    return thumbnail_path


def rotate_image(image_field):
    """
    Rotate (clockwise) the file associated with the given image_field.
    """
    pimage = PILImage.open(image_field.path)
    pimage = pimage.rotate(270)
    pimage.save(image_field.path)
    return True
