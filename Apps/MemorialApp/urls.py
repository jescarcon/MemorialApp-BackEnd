from rest_framework.routers import DefaultRouter
from .views import MediumViewSet
from .views import NoteViewSet
from .views import UserViewSet
from django.urls import path, include


router = DefaultRouter()
router.register(r'media', MediumViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]