from django.urls import path
from django.contrib import admin
from comparedata import views

urlpatterns = [
	path('', views.IndexView.as_view(), name='index'),
    path('admin/', admin.site.urls),
	path('oauth-response/', views.OAuthResponse.as_view(), name='oauth_response'),
    path('loading/<str:job_id>/', views.LoadingPage.as_view(), name='loading_page'), 
    path('select-object/<str:job_id>/', views.SelectObject.as_view(), name='select_object'),
    path('job-status/<str:job_id>/', views.job_status),
    path('get-fields/<str:job_id>/<int:object_id>/', views.get_fields),
    path('compare-data/<str:job_id>/<int:object_id>/', views.execute_data_compare),
    path('compare-data-result/<str:job_id>/', views.CompareDataResult.as_view(), name='compare_data_result'),
    path('unmatched-rows/<str:job_id>/<int:org_no>/', views.get_unmatched_rows),
]
