import os
import tempfile
import zipfile

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from photos.forms import AlbumForm, AlbumMergeForm
from photos.models import Album, Location
from photos.views import get_photo_queryset
from utils.paginate import paginate
from utils.views import json_redirect, json_render


def get_back_link(request, album, **kwargs):
    """
    Determines the back link for an album.
    - If the URL is /locations/<id>/albums/<id>/ then go back to the location.
    - If the URL is /albums/<id>/ then go back to the album list.
    """
    if 'location_pk' in kwargs:
        location = get_object_or_404(Location, pk=kwargs.get('location_pk'))
        return {
            'url': location.get_absolute_url(),
            'title': location.name
        }
    return {
        'url': reverse('albums'),
        'title': 'Albums'
    }


@login_required
def list(request):
    paginator, queryset = paginate(
        request, Album.objects.all(), settings.PHOTOS_PER_PAGE)
    context = {'paginator': paginator, 'album_list': queryset}
    return render(request, 'photos/album_list.html', context)


@login_required
def detail(request, pk, **kwargs):
    album = get_object_or_404(Album, pk=pk)
    paginator, queryset = paginate(
        request, get_photo_queryset(album=album), settings.PHOTOS_PER_PAGE)
    context = {
        'location_pk': kwargs.get('location_pk'),
        'album': album,
        'paginator': paginator,
        'photo_list': queryset,
        'back_link': get_back_link(request, album, **kwargs)
    }
    return render(request, 'photos/album_detail.html', context)


@permission_required('photos.add_album')
def create(request):
    form = AlbumForm(request.POST or None)
    if form.is_valid():
        album = form.save()
        return json_redirect(album.get_absolute_url())
    context = {
        'form': form,
        'form_title': 'Create Album',
        'form_submit': 'Save'
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.edit_album')
def edit(request, pk):
    album = get_object_or_404(Album, pk=pk)
    form = AlbumForm(request.POST or None, instance=album)
    if form.is_valid():
        album = form.save()
        return json_redirect(album.get_absolute_url())
    context = {
        'form': form,
        'form_title': 'Edit Album',
        'form_submit': 'Save'
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.delete_album')
def delete(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if request.POST:
        album.delete()
        return json_redirect(reverse('albums'))
    context = {
        'album': album,
        'form_title': 'Delete Album',
        'form_submit': 'Delete',
        'form_messages': (
            'Are you sure you want to delete this album?',
            'This will also delete all the photos in the album.'
        )
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.edit_album')
def merge(request, pk):
    album = get_object_or_404(Album, pk=pk)
    form = AlbumMergeForm(request.POST or None, instance=album)
    if form.is_valid():
        album = form.save()
        return json_redirect(album.get_absolute_url())
    context = {
        'album': album,
        'form_title': 'Merge Album',
        'form_submit': 'Merge'
    }
    return json_render(request, 'photos/ajax_form.html', context)


@login_required
def download(request, pk):
    album = get_object_or_404(Album, pk=pk)
    temp_zip = tempfile.NamedTemporaryFile()
    with zipfile.ZipFile(temp_zip, 'w') as zipf:
        for photo in album.photo_set.all():
            full_path = os.path.join(settings.MEDIA_ROOT, photo.file.name)
            zipf.write(full_path, '%s.%s' % (photo.file.name.split('/')[-1]))
    temp_zip.seek(0)
    response = HttpResponse(temp_zip.read(), content_type='application/zip')
    response['Content-Disposition'] = 'attachment; \
            filename=%s.zip' % album.name
    return response
