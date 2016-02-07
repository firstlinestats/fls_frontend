from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.teams, name='/team/teams'),
    url(r'^(?P<team_id>[0-9]+)/$', views.team_page, name='team_page'),
]