from django.urls import path

from .consumers import SalesConsumer

websocket_urlpatterns = [
    path("ws/sales/", SalesConsumer.as_asgi()),
]
