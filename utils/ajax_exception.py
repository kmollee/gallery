from django.conf import settings


class AJAXSimpleExceptionResponse:
    """
    If the request is an AJAX request, any errors will be printed to stdout.
    """
    def process_exception(self, request, exception):
        if settings.DEBUG and request.is_ajax():
            import sys
            import traceback
            (exc_type, exc_info, tb) = sys.exc_info()
            response = '%s\n' % exc_type.__name__
            response += '%s\n\n' % exc_info
            response += 'TRACEBACK:\n'
            for tb in traceback.format_tb(tb):
                response += '%s\n' % tb
            print(response)
