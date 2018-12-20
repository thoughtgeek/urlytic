from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^', include('home.urls', namespace='home_ns', app_name='home')),
    url(r'^filedetail/', include('filedetail.urls', namespace='filedetail_ns', app_name='filedetail')),
]
