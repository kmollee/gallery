from django.contrib import admin

from photos.models import Person, Location, Album, Photo, Thumbnail


class NameOnlyAdmin(admin.ModelAdmin):
    list_display = ['name', ]


class AlbumAdmin(admin.ModelAdmin):
    list_display = ['name', 'month', 'year', 'location', ]


class ThumbnailInline(admin.TabularInline):
    model = Thumbnail
    readonly_fields = ['file', ]


class PhotoAdmin(admin.ModelAdmin):
    list_display = ['name', 'album', ]
    inlines = [ThumbnailInline, ]


admin.site.register(Person, NameOnlyAdmin)
admin.site.register(Location, NameOnlyAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
