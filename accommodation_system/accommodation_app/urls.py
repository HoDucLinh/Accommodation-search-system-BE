from django.contrib import admin
from django.urls import path
from . import views
from .admin import admin_site

urlpatterns = [
    path('', views.index),
    path('admin/', admin_site.urls)
]