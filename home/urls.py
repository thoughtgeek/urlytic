from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^filelist$', views.filelist, name='filelist'),
    url(r'^logout$', views.log_out, name='log_out'),
    url(r'^registermember$', views.register, name='register'),

    url(r'^accounts/', include('django.contrib.auth.urls')),
]