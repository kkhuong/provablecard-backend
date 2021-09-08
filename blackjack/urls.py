from django.urls import path
from django.conf.urls import url, include 
from . import views

urlpatterns = [
    url(r'^api/hand$', views.hand_list),
    url(r'^api/hand/(?P<pk>[0-9]+)$', views.hand_detail),
]
