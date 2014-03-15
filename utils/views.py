import json

from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string


def json_render(request, template_name, context, **kwargs):
    """
    Returns a JSON response for displaying some HTML. This is very specific
    to this project and depends on the JavaScript supporting the result that
    is returned from this method.
    """
    kwargs['content_type'] = 'text/json'
    data = {
        'action': 'display',
        'html': render_to_string(
            template_name, context, context_instance=RequestContext(request))
    }
    return HttpResponse(json.dumps(data), **kwargs)


def json_redirect(url, **kwargs):
    """
    Returns a JSON response for redirecting to a new URL. This is very specific
    to this project and depends on the JavaScript supporting the result that
    is returned from this method.
    """
    kwargs['content_type'] = 'text/json'
    data = {'action': 'redirect', 'url': url}
    return HttpResponse(json.dumps(data), **kwargs)
