from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.users import views

router = DefaultRouter()

router.register(r"", views.UserViewSet)

urlpatterns = [] + router.urls
