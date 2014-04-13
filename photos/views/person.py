from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from photos.forms import PersonRenameForm
from photos.models import Person
from photos.views import get_photo_queryset
from stream.utils import send_action
from utils.paginate import paginate
from utils.views import json_redirect, json_render


@login_required
def list(request):
    paginator, queryset = paginate(
        request, Person.objects.all(), settings.PHOTOS_PER_PAGE)
    context = {'paginator': paginator, 'person_list': queryset}
    return render(request, 'photos/person_list.html', context)


@login_required
def detail(request, pk):
    person = get_object_or_404(Person, pk=pk)
    paginator, queryset = paginate(
        request, get_photo_queryset(person=person), settings.PHOTOS_PER_PAGE)
    context = {
        'person': person,
        'paginator': paginator,
        'photo_list': queryset,
        'back_link': {'url': reverse('people'), 'title': _('People')}
    }
    return render(request, 'photos/person_detail.html', context)


@permission_required('photos.delete_person')
def delete(request, pk):
    person = get_object_or_404(Person, pk=pk)
    if request.POST:
        person.delete()
        return json_redirect(request, reverse('people'))
    context = {
        'person': person,
        'form_title': _('Delete Person'),
        'form_submit': _('Delete'),
        'form_messages': (
            _('Are you sure you want to delete this person?'),
            _('This will also remove tags from any photos.')
        )
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.add_person')
def create(request):
    form = PersonRenameForm(request.POST or None)
    if form.is_valid():
        person = form.save()
        send_action(
            request.user,
            'created the person',
            target=person)
        return json_redirect(request, person.get_absolute_url())
    context = {
        'form': form,
        'form_title': _('Create Person'),
        'form_submit': _('Save')
    }
    return json_render(request, 'photos/ajax_form.html', context)


@permission_required('photos.edit_person')
def rename(request, pk):
    person = get_object_or_404(Person, pk=pk)
    form = PersonRenameForm(request.POST or None, instance=person)
    if form.is_valid():
        person = form.save()
        return json_redirect(request, person.get_absolute_url())
    context = {
        'form': form,
        'form_title': _('Rename Person'),
        'form_submit': _('Save')
    }
    return json_render(request, 'photos/ajax_form.html', context)
