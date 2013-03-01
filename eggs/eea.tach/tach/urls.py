from django.conf.urls import patterns, include, url
from tach import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'tach.views.home', name='home'),
    # url(r'^tach/', include('tach.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.Overview.as_view(), name='overview'),
    url(r'^survey$', views.Survey.as_view(), name='survey'),
)
