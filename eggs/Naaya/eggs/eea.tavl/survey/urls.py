from django.conf.urls import patterns, include, url
from survey import views

urlpatterns = patterns('',
    url(r'^section_a/(?P<category_id>[\d]+)$', views.SectionA.as_view(), name='section_a'),
)
