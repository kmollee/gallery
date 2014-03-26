from django.core.paginator import Paginator, InvalidPage
from django.http import Http404


def paginate(request, queryset, page_size, page_arg="p", allow_empty=True):
    """
    Paginates a queryset based on the arguments passed in. Returns the
    paginator instance and the object list for the current page. The paginator
    instance will also have a "this_page" variable that corresponds to the
    current page returned by the paginator.page() method.
    """
    paginator = Paginator(
        queryset, page_size, allow_empty_first_page=allow_empty)
    page_num = request.GET.get(page_arg, 1)

    try:
        page_num = int(page_num)
    except ValueError:
        page_num = 1

    try:
        page = paginator.page(page_num)
    except InvalidPage as e:
        raise Http404('Invalid page (%(page_num)s): %(message)s' % {
            'page_num': page_num,
            'message': str(e)
        })

    # Add our custom "this_page" and "page_arg" variables to this paginator.
    paginator.this_page = page
    paginator.page_arg = page_arg

    # Add our custom "previous_url" and "next_url" variables to this
    # paginator instance so that we don't need to build the URL in the
    # template, which is honestly kind of ugly.
    def build_page_url(num):
        get_params = request.GET.copy()
        get_params[page_arg] = num
        return '%s?%s' % (request.path, get_params.urlencode())

    paginator.previous_url = None
    if page.has_previous():
        paginator.previous_url = build_page_url(page.previous_page_number())

    paginator.next_url = None
    if page.has_next():
        paginator.next_url = build_page_url(page.next_page_number())

    return (paginator, page.object_list)
