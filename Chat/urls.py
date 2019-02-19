from django.urls import path
from django.shortcuts import redirect
from Chat.views.chatView import chat
from Chat.views.usersView import UserView
from Chat.views.channelView import ChannelView
from Chat.views.messagesView import MessageView

urlpatterns = [
    path('api/', chat),
    path('api/user/', UserView.as_view()),
    path('api/channels/', ChannelView.as_view()),
    path('api/<slug:channel_url>/messages/', MessageView.as_view()),
]