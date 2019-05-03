from django.urls import path, re_path
from Chat.consumers import ChatConsumer
websocket_urlpatterns = [
    path('ws/api/<slug:channel_url>/', ChatConsumer)
]