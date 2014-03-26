import logging

from django.conf import settings


class ExceptionLoggingMiddleware:
    """
    Log all view exceptions in DEBUG mode.
    """
    def process_exception(self, request, exception):
        if settings.DEBUG:
            logging.exception(
                'ExceptionLoggingMiddleware for %s' % request.path)
