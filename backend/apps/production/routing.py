from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/production/', consumers.ProductionConsumer.as_asgi()),
]
