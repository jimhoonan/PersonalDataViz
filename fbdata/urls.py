from django.urls import path
from django.contrib import admin

from . import views

urlpatterns = [
path('', views.home, name='home'),
path('uploader', views.uploader, name='uploader'),
path('graph', views.graph, name='graph')
]