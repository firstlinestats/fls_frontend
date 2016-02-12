from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^skaters/$', views.skaters, name='/player/skaters'),
]