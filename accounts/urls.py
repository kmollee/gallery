from django.conf.urls import patterns, url

from accounts import views

urlpatterns = patterns(
    '',
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/(?P<auth>[\w]+)/$', views.register, name='register'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^password/reset/$', views.password_reset, name='password_reset'),
    url(r'^password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^password/change/$', views.password_change, name='password_change'),
)
