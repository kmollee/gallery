from django.conf.urls import patterns, url

urlpatterns = patterns(
    'accounts.views',
    url(r'^login/$', 'login', name='login'),
    url(r'^logout/$', 'logout', name='logout'),
    url(r'^register/$', 'register', name='register'),
    url(r'^register/(?P<auth>[\w]+)/$', 'register', name='register'),
    url(r'^profile/$', 'profile', name='profile'),
    url(r'^password/reset/$', 'password_reset', name='password_reset'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'password_reset_confirm', name='password_reset_confirm'),
    url(r'^password/change/$', 'password_change', name='password_change'),
)
