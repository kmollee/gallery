import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _

from utils.filestorage.uploads import get_unique_upload_path
from utils.filestorage.signals import delete_files_on_delete, \
    delete_files_on_change
from stream.models import ActionableModel
from photos.utils import generate_thumbnail

MONTH_CHOICES = ((mon, datetime.date(2000, mon, 1).strftime('%B')) for mon in
                 range(1, 13))

YEAR_CHOICES = ((year, year) for year in
                range(1950, (datetime.datetime.now().year + 1)))


class Location(ActionableModel):
    """A location is a physical location that can be applied to an album."""

    name = models.CharField(_('name'), max_length=200)

    class Meta:
        ordering = ['name', ]
        verbose_name = _('location')
        verbose_name_plural = _('locations')

    @models.permalink
    def get_absolute_url(self):
        return ('location', [str(self.id)])

    def __str__(self):
        return self.name

    @property
    def cover_photo(self):
        """
        Returns the cover photo for this person, which for now is just the
        first photo from the first album based on whatever ordering is the
        default.
        """
        return self.album_set.first().photo_set.first()


class Person(ActionableModel):
    """A person is an actual person that can be tagged in photos."""

    name = models.CharField(_('name'), max_length=200)

    class Meta:
        ordering = ['name', ]
        verbose_name = _('person')
        verbose_name_plural = _('people')

    @models.permalink
    def get_absolute_url(self):
        return ('person', [str(self.id)])

    def __str__(self):
        return self.name

    @property
    def cover_photo(self):
        """
        Returns the cover photo for this person, which for now is just the
        first photo based on whatever ordering is the default.
        """
        return self.photo_set.first()


class Album(ActionableModel):
    """
    An album is a collection of photos. It belongs to a location and can also
    have a month and a year associated with it.
    """

    name = models.CharField(_('name'), max_length=200)
    month = models.PositiveSmallIntegerField(
        _('month'), null=True, blank=True, choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField(
        _('year'), null=True, blank=True, choices=YEAR_CHOICES)

    location = models.ForeignKey(
        Location, null=True, blank=True,
        verbose_name=_('location'), on_delete=models.SET_NULL)

    class Meta:
        ordering = ['name', ]
        verbose_name = _('album')
        verbose_name_plural = _('albums')

    @models.permalink
    def get_absolute_url(self):
        return ('album', [str(self.id)])

    def __str__(self):
        return self.name

    @property
    def cover_photo(self):
        """
        Returns the cover photo for this album, which for now is just the
        first photo based on whatever ordering is the default.
        """
        return self.photo_set.first()

    def get_date_display(self):
        """
        Returns a pretty display of the month and year in one of the formats:
        - 'January 2014'
        - 'January'
        - '2014'
        """
        output = []
        if self.month:
            output.append(str(self.get_month_display()))
        if self.year:
            output.append(str(self.get_year_display()))
        return ' '.join(output)


class Photo(ActionableModel):
    """
    A photo is just that - a single photo. It can belong to only one album.
    """

    name = models.CharField(_('name'), max_length=200, null=True, blank=True)
    file = models.ImageField(_('file'), upload_to=get_unique_upload_path)

    album = models.ForeignKey(Album, verbose_name=_('album'))
    people = models.ManyToManyField(
        Person, blank=True, verbose_name=_('people'))

    # exif_make = models.CharField(max_length=100, null=True, blank=True)
    # exif_model = models.CharField(max_length=100, null=True, blank=True)
    # exif_iso = models.PositiveSmallIntegerField(null=True, blank=True)
    # exif_focal = models.PositiveSmallIntegerField(null=True, blank=True)
    # exif_exposure = models.CharField(max_length=100, null=True, blank=True)
    # exif_fnumber = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['name', ]
        verbose_name = _('photo')
        verbose_name_plural = _('photos')

    @models.permalink
    def get_absolute_url(self):
        return ('photo', [str(self.id)])

    def __str__(self):
        return self.name

    def thumbnail(self, size):
        """
        Generate and return a thumbnail with the given size. Only do this once
        in this instance to save on hits to the Thumnail model.
        """
        prop_name = '_thumbnail_%s' % size.replace('-', '_')
        if not hasattr(self, prop_name):
            setattr(
                self,
                prop_name,
                self.thumbnail_set.get_or_create(size=size)[0].file)
        return getattr(self, prop_name)

    @property
    def file_200x200(self):
        """
        Shortcut to generate a '200x200-fit' thumbnail. Useful in templates.
        """
        return self.thumbnail('200x200-fit')

    @property
    def file_800x600(self):
        """
        Shortcut to generate a '800x600-thumb' thumbnail. Useful in templates.
        """
        return self.thumbnail('800x600-thumb')


class Thumbnail(models.Model):
    """
    A thumbnail is a smaller resolution size of a photo. It knows how to
    generate itself once it has a size and a photo associated to it.
    """

    size = models.CharField(_('size'), max_length=20, db_index=True)
    file = models.ImageField(_('file'))
    photo = models.ForeignKey(Photo, verbose_name=_('photo'))

    class Meta:
        ordering = ['photo', 'size', ]
        unique_together = ('photo', 'size', )
        verbose_name = _('thumbnail')
        verbose_name_plural = _('thumbnails')

    def __str__(self):
        return '%s (%s)' % (self.photo, self.size)

    def generate(self):
        """
        Generate the thumbnail. This happens regardless of whether we already
        have one generated. The new one will overwrite the existing one (while
        keeping the same filename).
        """
        self.file = generate_thumbnail(self.photo.file, self.size)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        If we have a photo and a size, generate a thumbnail regardless of
        whether we already have one generated. Maybe in the future this could
        check to make sure the thumbnail already exists, but that's
        not needed now.
        """
        if self.photo and self.size:
            self.generate()
        super().save(force_insert, force_update, using, update_fields)


models.signals.pre_delete.connect(delete_files_on_delete, sender=Photo)
models.signals.pre_save.connect(delete_files_on_change, sender=Photo)

models.signals.pre_delete.connect(delete_files_on_delete, sender=Thumbnail)
models.signals.pre_save.connect(delete_files_on_change, sender=Thumbnail)
