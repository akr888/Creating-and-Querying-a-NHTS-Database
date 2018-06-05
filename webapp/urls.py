from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
	url(r'^contact/', views.contact, name='contact'),
	url(r'^nonquery/state/chart', views.chart, name='chart'),
    url(r'^output/', views.output, name='output'),
	url(r'^nonquery/state/stateaction', views.stateaction, name='stateaction'),
	url(r'^nonquery/ethnicity/avgtriprace', views.avgtriprace, name='avgtriprace'),
	url(r'^nonquery/urbanrural/avgtripUR', views.avgtripUR, name='avgtripUR'),
    url(r'^nonquery/urbanrural', views.urbanrural, name='urbanrural'),
	url(r'^nonquery/weightedurbanrural', views.weightedurbanrural, name='weightedurbanrural'),
	url(r'^nonquery/urbanrural/weightedavgtripUR', views.weightedavgtripUR, name='weightedavgtripUR'),
	url(r'^nonquery/', views.nonquery, name='nonquery'),
	url(r'^some_view/', views.some_view, name='some_view'),
	
    ]