"""sfdatacompare URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from comparedata import views

urlpatterns = [
	url(r'^admin/', include(admin.site.urls)),
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^oauth-response/$', views.OAuthResponse.as_view(), name='oauth_response'),
    url(r'^query-objects/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.QueryObjects.as_view(), name='query_objects'),
    url(r'^select-object/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.SelectObject.as_view(), name='select_object'),
    url(r'^job-status/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'comparedata.views.job_status'),
    url(r'^get-fields/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'comparedata.views.get_fields'),
    url(r'^get-fields-status/(?P<field_job_id>\d+)/$', 'comparedata.views.get_fields_job_status'),
]
