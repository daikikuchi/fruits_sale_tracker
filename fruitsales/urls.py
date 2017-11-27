from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^main/$', views.MainView.as_view(), name='main'),
    url(r'^fruit/admin/$', views.FruitListView.as_view(), name='fruit_admin_list'),
    url(r'^fruit/new/$', views.CreateFruitInfoView.as_view(), name='fruit_new'),
    url(r'^fruit/(?P<pk>\d+)/edit/$',
        views.FruitInfoUpdateView.as_view(), name='fruit_edit'),
    url(r'^fruit/(?P<pk>\d+)/delete/$',
        views.FruitInfoDeleteView.as_view(), name='fruit_delete'),
    url(r'^fruitsales/admin/$', views.FruitSalesListView.as_view(),
        name='fruitsales_admin_list'),
    url(r'^fruitsales/new/$', views.CreateFruitSalesView.as_view(),
        name='fruitsales_new'),
    url(r'^fruitsales/(?P<pk>\d+)/edit/$',
        views.FruitSalesInfoUpdateView.as_view(), name='fruitsales_edit'),
    url(r'^fruitsales/(?P<pk>\d+)/delete/$',
        views.FruitSalesDeleteView.as_view(), name='fruitsales_delete'),
    url(r'^upload/$', views.upload_csv, name='upload_csv'),
    url(r'^fruitsalesstats/$', views.sale_stats, name='fruitsales_admin_stats'),
]
