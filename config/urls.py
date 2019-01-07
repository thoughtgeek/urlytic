from django.conf.urls import url, include
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^', include('apps.urlytic.urls')),
]
