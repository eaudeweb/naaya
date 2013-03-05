from django.conf.urls import patterns, include, url
from tach import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.Overview.as_view(), name='overview'),
    url(r'^survey$', views.Survey.as_view(), name='survey_overview'),
    url(r'^survey/', include('survey.urls', namespace='survey')),
)
