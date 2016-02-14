from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^skaters/$', views.skaters, name='/player/skaters'),
    url(r'^player/(?P<player_id>\d+)/$', views.player),
    url(r'^skater_list_table/$', views.skatersTable)
]