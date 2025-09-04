from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OperationalCenterViewSet

router = DefaultRouter()
router.register(r'operational-centers', OperationalCenterViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
