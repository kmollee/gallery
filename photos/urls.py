from django.conf.urls import patterns, url

urlpatterns = patterns(
    'photos.views',
    url(r'^upload/$', 'upload', name='upload'),
    url(r'^search/$', 'search', name='search'),
    url(r'^search/(?P<query>[\w=&]+)/$', 'results', name='results'),

    url(r'^albums/$', 'album.list', name='albums'),
    url(r'^albums/create.ajax/$', 'album.create', name='album_create'),
    url(r'^albums/(?P<pk>\d+)/$', 'album.detail', name='album'),
    url(r'^albums/(?P<pk>\d+)/edit.ajax/$', 'album.edit', name='album_edit'),
    url(r'^albums/(?P<pk>\d+)/delete.ajax/$', 'album.delete',
        name='album_delete'),
    url(r'^albums/(?P<pk>\d+)/merge.ajax/$', 'album.merge',
        name='album_merge'),
    url(r'^albums/(?P<pk>\d+)/download/$', 'album.download',
        name='album_download'),

    url(r'^locations/$', 'location.list', name='locations'),
    url(r'^locations/create.ajax/$', 'location.create',
        name='location_create'),
    url(r'^locations/(?P<pk>\d+)/$', 'location.detail', name='location'),
    url(r'^locations/(?P<pk>\d+)/rename.ajax/$', 'location.rename',
        name='location_rename'),
    url(r'^locations/(?P<pk>\d+)/delete.ajax/$', 'location.delete',
        name='location_delete'),

    url(r'^people/$', 'person.list', name='people'),
    url(r'^people/create.ajax/$', 'person.create', name='person_create'),
    url(r'^people/(?P<pk>\d+)/$', 'person.detail', name='person'),
    url(r'^people/(?P<pk>\d+)/rename.ajax/$', 'person.rename',
        name='person_rename'),
    url(r'^people/(?P<pk>\d+)/delete.ajax/$', 'person.delete',
        name='person_delete'),

    url(r'^photos/(?P<pk>\d+)/$', 'photo.detail', name='photo'),
    url(r'^photos/(?P<pk>\d+)/rotate.ajax/$', 'photo.rotate',
        name='photo_rotate'),
    url(r'^photos/(?P<pk>\d+)/move.ajax/$', 'photo.move', name='photo_move'),
    url(r'^photos/(?P<pk>\d+)/rename.ajax/$', 'photo.rename',
        name='photo_rename'),
    url(r'^photos/(?P<pk>\d+)/tag.ajax/$', 'photo.tag', name='photo_tag'),
    url(r'^photos/(?P<pk>\d+)/delete.ajax/$', 'photo.delete',
        name='photo_delete'),
    url(r'^photos/(?P<pk>\d+)/download/$', 'photo.download',
        name='photo_download'),

    # alternate ways to get to an album
    url(r'^locations/(?P<location_pk>\d+)/albums/(?P<pk>\d+)/$',
        'album.detail', name='album'),

    # alternate ways to get to a photo
    url(
        r'^locations/(?P<location_pk>\d+)/albums/(?P<album_pk>\d+)/photos/(?P<pk>\d+)/$',
        'photo.detail', name='photo'),
    url(r'^people/(?P<person_pk>\d+)/photos/(?P<pk>\d+)/$', 'photo.detail',
        name='photo'),
    url(r'^search/(?P<query>[\w=&]+)/photos/(?P<pk>\d+)/$', 'photo.detail',
        name='photo'),
)
