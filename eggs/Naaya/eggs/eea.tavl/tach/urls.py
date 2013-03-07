from django.conf.urls import patterns, include, url
from tach import views
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.Overview.as_view(), name='overview'),
    url(r'^survey$', views.Survey.as_view(), name='survey_overview'),
    url(r'^survey/', include('survey.urls', namespace='survey')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
