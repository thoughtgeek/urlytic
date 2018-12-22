from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    url(r'^details/$', views.filedetail, name='filedetail_home'),
    url(r'^redirect/(?P<link>[a-zA-Z0-9]+)$', views.expand, name='shortlink'),

]