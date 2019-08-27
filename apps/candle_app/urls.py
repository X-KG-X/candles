from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^add/(?P<quantity>\d+)/(?P<product_id>\d+)$', views.add),
    url(r'^detail/(?P<product_id>\d+)$', views.detail),
    url(r'^$', views.index),
    url(r'^check_login$', views.check_login),
    url(r'^check_registration$',views.check_registration),
    url(r'^dashboard$',views.dashboard),
    url(r'^logoff$', views.logoff),

]