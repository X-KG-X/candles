from django.conf.urls import url
from . import views

urlpatterns=[
    url(r'^buy$', views.buy),
    url(r'^remove/(?P<product_id>\d+)$', views.remove),
    url(r'^history$', views.history),
    url(r'^cart$',views.cart),
    url(r'^add/(?P<product_id>\d+)$', views.add),
    url(r'^detail/(?P<product_id>\d+)$', views.detail),
    url(r'^$', views.index),
    url(r'^check_login$', views.check_login),
    url(r'^check_registration$',views.check_registration),
    url(r'^dashboard$',views.dashboard),
    url(r'^logoff$', views.logoff),

    url(r'^search_item$', views.search_item), # search item with string from search bar
    url(r'^search_ajax$', views.search_ajax), # show auto populated result while typing in search bar
    url(r'^update_select_options/(?P<product_id>\d+)$', views.update_select_options),

    url(r'^google_login', views.google_login),
]