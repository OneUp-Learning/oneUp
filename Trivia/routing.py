
from django.urls import path, re_path
from Trivia.consumers import TriviaConsumer

websocket_urlpatterns = [
    path('ws/trivia/<slug:trivia_id>', TriviaConsumer)
]