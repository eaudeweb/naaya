from django.conf.urls import patterns, include, url
from survey import views

urlpatterns = patterns('',
    url(r'^section/(?P<category_id>[\d]+)/view/(?P<survey_id>[\d]+)/$', views.View.as_view(), name='view'),
    url(r'^section/(?P<category_id>[\d]+)/edit/$', views.Edit.as_view(), name='edit'),
)
