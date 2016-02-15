from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.game_list, name='/playbyplay/game_list'),
    url(r'^(?P<game_pk>[0-9]+)/$', views.game_page, name='game_page'),
    url(r'^game_list_table/$', views.game_list_table, name='game_page'),
    url(r'^game_tables$', views.game_tables, name='game_tables')
]