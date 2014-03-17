import mimetypes

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from photos.forms import PhotoMoveForm, PhotoRenameForm, PhotoTagForm
from photos.models import Person, Photo
from photos.utils import rotate_image
from photos.views import get_photo_queryset
from utils.views import json_redirect, json_render


def get_back_link(request, photo, **kwargs):
    """
    Determines the back link for a photo.
    - If the URL is /locations/<id>/albums/<id>/photos/<id>/ then go back to
      the album within the context of location.
    - If the URL is /people/<id>/photos/<id> then go back to the person.
    - If the URL is /search/<query>/photos/<id> then go back to the search.
    - If the URL is /photos/<id> then go back to the album.
    """
    if 'person_pk' in kwargs:
        person = get_object_or_404(Person, pk=kwargs['person_pk'])
        return {
            'url': reverse('person', kwargs={'pk': person.pk}),
            'title': person.name
        }
    if 'location_pk' in kwargs:
        new_kwargs = {'pk': photo.album.pk,
                      'location_pk': kwargs['location_pk']}
        return {
            'url': reverse('album', kwargs=new_kwargs),
            'title': photo.album.name
        }
    if 'query' in kwargs:
        return {
            'url': reverse('results', kwargs={'query': kwargs['query']}),
            'title': 'Results'
        }
    return {
        'url': reverse('album', kwargs={'pk': photo.album.pk}),
        'title': photo.album.name
    }


def get_paginator(request, photo, **kwargs):
    """
    This is a big messy function that I should probably revisit some day. Here
    is what it tries to accomplish:
    We need to figure out where this photo is (index) in the queryset. The
    problem is that queryset is variable. If the user came from an album, then
    the queryset is the album's list of photos. If the user came from a person,
    then the queryset is the person's list of photos. If the user came from
    search, then the queryset is the search results list. This also impacts the
    'next' and 'previous' URLs which need to know about the current context as
    well. So that's what this does. Fancy.
    """
    if 'person_pk' in kwargs:
        person = get_object_or_404(Person, pk=kwargs['person_pk'])
        queryset = get_photo_queryset(person=person)
    elif 'query' in kwargs:
        queryset = get_photo_queryset(query=kwargs['query'])
    else:
        queryset = get_photo_queryset(album=photo.album)

    # We really only need the list of sorted names and IDs.
    values_list = list(queryset.order_by('name').values_list('id', 'name'))
    index = values_list.index((photo.pk, photo.name))

    def build_url(pk):
        url_kwargs = kwargs.copy()
        url_kwargs['pk'] = pk
        return reverse('photo', kwargs=url_kwargs)

    next_url, prev_url = None, None
    if len(values_list) > 1:
        if index != len(values_list) - 1:  # not last
            next_url = build_url(values_list[index + 1][0])
        if index != 0:  # not first
            prev_url = build_url(values_list[index - 1][0])

    return {
        'has_next': (next_url is not None),
        'next_url': next_url,
        'has_previous': (prev_url is not None),
        'previous_url': prev_url,
        'index': (index + 1),
        'count': len(values_list)
    }


@login_required
def detail(request, pk, **kwargs):
    photo = get_object_or_404(Photo, pk=pk)
    context = {
        'photo': photo,
        'back_link': get_back_link(request, photo, **kwargs),
        'paginator': get_paginator(request, photo, **kwargs),
    }
    return render(request, 'photos/photo_detail.html', context)


@permission_required('photos.edit_photo')
def rotate(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.POST:
        rotate_image(photo.file)
        for thumb in photo.thumbnail_set.all():
            rotate_image(thumb.file)
    return json_redirect(photo.get_absolute_url())


@permission_required('photos.edit_photo')
def move(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    form = PhotoMoveForm(request.POST or None, instance=photo)
    if form.is_valid():
        photo = form.save()
        return json_redirect(photo.get_absolute_url())
    context = {
        'form': form,
        'form_title': 'Move Photo',
        'form_submit': 'Save'
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.edit_photo')
def rename(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    form = PhotoRenameForm(request.POST or None, instance=photo)
    if form.is_valid():
        photo = form.save()
        return json_redirect(photo.get_absolute_url())
    context = {
        'form': form,
        'form_title': 'Rename Photo',
        'form_submit': 'Save'
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.edit_photo')
def tag(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    form = PhotoTagForm(request.POST or None, instance=photo)
    if form.is_valid():
        photo = form.save()
        return json_redirect(photo.get_absolute_url())
    context = {
        'form': form,
        'form_title': 'Tag Photo',
        'form_submit': 'Save'
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.delete_photo')
def delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    if request.POST:
        next_url = photo.album.get_absolute_url()
        photo.delete()
        return json_redirect(next_url)
    context = {
        'photo': photo,
        'form_title': 'Delete Photo',
        'form_submit': 'Delete',
        'form_messages': (
            'Are you sure you want to delete this photo?',
        )
    }
    return json_render(request, 'photos/ajax_form.html', context)


@login_required
def download(request, pk):
    photo = get_object_or_404(Photo, pk=pk)
    file_data = photo.file.file.read()
    mimetype = mimetypes.guess_type(photo.file.name, strict=False)[0]
    response = HttpResponse(file_data, content_type=mimetype)
    response['Content-Disposition'] = 'attachment; \
            filename=%s' % photo.file.name.split('/')[-1]
    return response
