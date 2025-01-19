from django.urls import path
from .consumers import SyncTokenConsumer

websocket_urlpatterns = [
    path("ws/socket.io/", SyncTokenConsumer.as_asgi()),
]
