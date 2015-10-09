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
    url(r'^loading/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.LoadingPage.as_view(), name='loading_page'), 
    url(r'^select-object/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.SelectObject.as_view(), name='select_object'),
    url(r'^job-status/(?P<job_id>[0-9A-Za-z_\-]+)/$', 'comparedata.views.job_status'),
    url(r'^get-fields/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_id>\d+)/$', 'comparedata.views.get_fields'),
    url(r'^compare-data/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<object_id>\d+)/$', 'comparedata.views.execute_data_compare'),
    url(r'^compare-data-result/(?P<job_id>[0-9A-Za-z_\-]+)/$', views.CompareDataResult.as_view(), name='compare_data_result'),
    url(r'^unmatched-rows/(?P<job_id>[0-9A-Za-z_\-]+)/(?P<org_no>\d+)/$', 'comparedata.views.get_unmatched_rows'),
]
