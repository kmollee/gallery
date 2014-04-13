from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from photos.forms import LocationRenameForm
from photos.models import Location
from stream.utils import send_action
from utils.paginate import paginate
from utils.views import json_redirect, json_render


@login_required
def list(request):
    paginator, queryset = paginate(
        request, Location.objects.all(), settings.PHOTOS_PER_PAGE)
    context = {'paginator': paginator, 'location_list': queryset}
    return render(request, 'photos/location_list.html', context)


@login_required
def detail(request, pk):
    location = get_object_or_404(Location, pk=pk)
    paginator, queryset = paginate(
        request, location.album_set.all(), settings.PHOTOS_PER_PAGE)
    context = {
        'location': location,
        'paginator': paginator,
        'album_list': queryset,
        'back_link': {'url': reverse('locations'), 'title': _('Locations')}
    }
    return render(request, 'photos/location_detail.html', context)


@permission_required('photos.add_location')
def create(request):
    form = LocationRenameForm(request.POST or None)
    if form.is_valid():
        location = form.save()
        send_action(
            request.user,
            'created the location',
            target=location)
        return json_redirect(request, location.get_absolute_url())
    context = {
        'form': form,
        'form_title': _('Create Location'),
        'form_submit': _('Save')
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.edit_location')
def rename(request, pk):
    location = get_object_or_404(Location, pk=pk)
    form = LocationRenameForm(request.POST or None, instance=location)
    if form.is_valid():
        location = form.save()
        return json_redirect(request, location.get_absolute_url())
    context = {
        'form': form,
        'form_title': _('Rename Location'),
        'form_submit': _('Save')
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.delete_location')
def delete(request, pk):
    location = get_object_or_404(Location, pk=pk)
    if request.POST:
        location.delete()
        return json_redirect(request, reverse('locations'))
    context = {
        'location': location,
        'form_title': _('Delete Location'),
        'form_submit': _('Delete'),
        'form_messages': (
            _('Are you sure you want to delete this location?'),
            _('This will also remove this location from any albums.')
        )
    }
    return json_render(request, 'photos/ajax_form.html', context)
