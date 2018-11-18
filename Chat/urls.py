from django.urls import path
from Chat.api_endpoints import MessageView, ChannelView, UserView
from Chat.views.chatView import chatView

urlpatterns = [
    path('', chatView),
    path('api/user/', UserView.as_view()),
    path('api/channels/', ChannelView.as_view()),
    path('api/<slug:channel_url>/messages/', MessageView.as_view()),
]