from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import redirect, render

from photos.forms import UploadForm, SearchForm
from photos.models import Photo
from stream.utils import send_action
from utils.paginate import paginate


def get_photo_queryset(album=None, query=None, person=None):
    if album:
        return album.photo_set.all()
    if person:
        return person.photo_set.all()
    if query:
        query_dict = QueryDict(query)
        queryset = Photo.objects.all()
        q = query_dict.get('q')
        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | Q(album__name__icontains=q))
        a = query_dict.getlist('a')
        if a:
            queryset = queryset.filter(album__in=a)
        p = query_dict.getlist('p')
        if p:
            queryset = queryset.filter(people__in=p)
        l = query_dict.getlist('l')
        if l:
            queryset = queryset.filter(album__location__in=l)
        return queryset


@permission_required('photos.add_photo')
def upload(request):
    form = UploadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        album = form.save()
        send_action(
            request.user,
            'added %s photos to the album' % form.photo_count,
            target=album)
        return redirect(album.get_absolute_url())
    context = {'form': form}
    return render(request, 'photos/upload.html', context)


@login_required
def results(request, query):
    queryset = get_photo_queryset(query=query)
    paginator, queryset = paginate(request, queryset, settings.PHOTOS_PER_PAGE)
    context = {
        'query': query,
        'paginator': paginator,
        'photo_list': queryset,
        'back_link': {'url': reverse('search'), 'title': 'Search'}
    }
    return render(request, 'photos/search_results.html', context)


@login_required
def search(request):
    form = SearchForm(request.POST or None)
    if request.POST:
        post_copy = request.POST.copy()
        if 'csrfmiddlewaretoken' in post_copy:
            del post_copy['csrfmiddlewaretoken']
        return redirect(reverse('results',
                                kwargs={'query': post_copy.urlencode()}))
    context = {'form': form}
    return render(request, 'photos/search.html', context)
