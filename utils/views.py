from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string


def json_render(request, template_name, context, **kwargs):
    """
    Returns a JSON response for displaying some HTML. This is very specific
    to this project and depends on the JavaScript supporting the result that
    is returned from this method.
    """
    if not request.is_ajax():
        raise PermissionDenied("Must be an AJAX request.")
    data = {
        'action': 'display',
        'html': render_to_string(
            template_name, context, context_instance=RequestContext(request))
    }
    return JsonResponse(data, **kwargs)


def json_redirect(url, **kwargs):
    """
    Returns a JSON response for redirecting to a new URL. This is very specific
    to this project and depends on the JavaScript supporting the result that
    is returned from this method.
    """
    if not request.is_ajax():
        raise PermissionDenied("Must be an AJAX request.")
    data = {'action': 'redirect', 'url': url}
    return JsonResponse(data, **kwargs)
