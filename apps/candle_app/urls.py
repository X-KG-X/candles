from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^remove/(?P<order_id>\d+)$', views.remove),
    url(r'^history$', views.history),
    url(r'^cart$',views.cart),
    url(r'^add/(?P<product_id>\d+)$', views.add),
    url(r'^detail/(?P<product_id>\d+)$', views.detail),
    url(r'^$', views.index),
    url(r'^check_login$', views.check_login),
    url(r'^check_registration$',views.check_registration),
    url(r'^dashboard$',views.dashboard),
    url(r'^logoff$', views.logoff),

]