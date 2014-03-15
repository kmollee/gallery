from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelform_factory

from photos.models import Album, Photo, Location, Person
from photos.utils import file_allowed, friendly_filename


AlbumForm = modelform_factory(Album,
                              fields=['name', 'month', 'year', 'location'])
LocationRenameForm = modelform_factory(Location, fields=['name', ])
PersonRenameForm = modelform_factory(Person, fields=['name', ])
PhotoRenameForm = modelform_factory(Photo, fields=['name', ])
PhotoTagForm = modelform_factory(Photo, fields=['people', ])
PhotoMoveForm = modelform_factory(Photo, fields=['album', ])


class AlbumMergeForm(forms.Form):
    """
    A form to merge an album with another album. Merging an album moves all the
    photos to the new album and deletes the original album.
    """

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        super().__init__(*args, **kwargs)
        self.fields['new_album'] = forms.ModelChoiceField(
            label=_('New album'),
            queryset=Album.objects.exclude(pk=self.instance.pk))

    def save(self, commit=True):
        """
        Move all the photos from this album to the new album, then delete this
        album, then return the new album.
        """
        # Move all the photos from this album to the new album
        new_album = self.cleaned_data['new_album']
        self.instance.photo_set.all().update(album=new_album)
        # Delete this album
        self.instance.delete()
        # Return the new album
        return new_album


class SearchForm(forms.Form):
    """
    A form to search for photos. Can search by album, location, people, or a
    custom query.
    """

    a = forms.ModelMultipleChoiceField(
        label=_('Albums'), queryset=Album.objects.all())
    p = forms.ModelMultipleChoiceField(
        label=_('People'), queryset=Person.objects.all())
    l = forms.ModelMultipleChoiceField(
        label=_('Locations'), queryset=Location.objects.all())
    q = forms.CharField(label=_('Search'))


class UploadForm(forms.Form):
    """
    A form to upload photos. Right now a new album must always be created. This
    is only the case because I have not figured out an elegant way to allow
    creating or selecting an album.
    """

    album = forms.ModelChoiceField(queryset=Album.objects.all())
    photos = forms.FileField(label=_('Photos'))

    class Meta:
        fields = ['album', 'photos']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Change the photos widget to allow multiple files.
        self.fields['photos'].widget.attrs['multiple'] = 'multiple'

    def clean_photos(self):
        """
        Make sure each photo uploaded is allowed, according to the
        file_allowed function.
        """
        files_not_allowed = []
        for file_handle in self.files.getlist('photos'):
            if not file_allowed(file_handle.name):
                files_not_allowed.append(file_handle.name)
        if files_not_allowed:
            raise forms.ValidationError(
                _('The following files are not allowed: %s')
                % ', '.join(files_not_allowed))
        return self.cleaned_data['photos']

    def save(self):
        """
        Add each photo to the album (which must already be existing).
        TODO: support for zip file uploading.
        """
        self.instance = self.cleaned_data['album']
        self.photo_count = 0
        for file_handle in self.files.getlist('photos'):
            self.photo_count = self.photo_count + 1
            photo_name = friendly_filename(file_handle.name)
            photo = Photo.objects.create(
                album=self.instance, name=photo_name, file=file_handle)
            photo.thumbnail('200x200-fit')
        return self.instance
