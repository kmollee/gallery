from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings

from stream.views import action_list

urlpatterns = patterns(
    '',
    url(r'^$', action_list, name='home'),
    url(r'^auth/', include('accounts.urls', 'accounts')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('photos.urls')),
)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
