__author__ = 'MBK'

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name="api_index"),
]