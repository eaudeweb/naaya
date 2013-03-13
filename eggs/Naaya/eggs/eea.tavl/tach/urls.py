from django.conf.urls import patterns, include, url
from tach import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',

    url(r'^$', views.Overview.as_view(), name='overview'),

    url(r'^survey/$', views.Survey.as_view(), name='survey_overview'),

    url(r'^survey/', include('survey.urls', namespace='survey')),

    url(r'^manage/', include(admin.site.urls)),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
