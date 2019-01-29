from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.models import Channel, Message
from Chat.serializers import MessageSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import json, re
from django.shortcuts import redirect
from Instructors.views.utils import initialContextDict

class MessageView(APIView):
    renderer_classes = (JSONRenderer, )
    
    def get(self, request, channel_url, format=None):
        """
        Return a list of all messages.
        """
        context_dict, current_course = initialContextDict(request)
        channel = Channel.objects.get(channel_url=channel_url, course=current_course)
        # We want to show the last 25 messages, ordered most-recent-last
        messages = Message.objects.filter(channel=channel).order_by('-timestamp')
        paginator = Paginator(messages, 25)
        page = int(request.GET.get('page', 1))

        if page >= paginator.num_pages+1:
            return Response({})

        m = paginator.get_page(page)
    
        serializer = MessageSerializer(m, many=True)
        return Response(serializer.data)

