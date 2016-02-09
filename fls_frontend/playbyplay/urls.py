from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.games, name='/playbyplay/games'),
    url(r'^(?P<game_pk>[0-9]+)/$', views.game_page, name='game_page'),
]