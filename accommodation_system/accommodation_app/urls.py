from django.contrib import admin
from django.urls import path, include
from . import views
from .admin import admin_site
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register('accommodations' , views.AccommodationViewSet)
router.register('user', UserViewSet)
router.register('post',PostViewSet)
router.register('notification',views.NotificationsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin_site.urls)
]