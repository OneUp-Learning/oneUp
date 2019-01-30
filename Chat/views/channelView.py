from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.models import Channel
from Chat.serializers import ChannelSerializer, UserSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import json, re
from django.shortcuts import redirect
from Instructors.views.utils import initialContextDict

class ChannelView(APIView):
    renderer_classes = (JSONRenderer, )

    def get(self, request, format=None):
        """
        Return a list of all rooms.
        """
        context_dict, currentCourse = initialContextDict(request)
        channels = Channel.objects.filter(course=currentCourse)
        user = request.user

        subscribed_channels = Channel.objects.filter(users=user, course=currentCourse)
        # print("Sub Channels: {}".format(subscribed_channels))
        # print("All Channels: {}".format(channels))
    
        channels_serializer = ChannelSerializer(channels, many=True)
        sub_channel_serializer = ChannelSerializer(subscribed_channels, many=True)
        response = {
            'all_channels': channels_serializer.data,
            'subscribed_channels': sub_channel_serializer.data
        }
        return Response(response)

    def post(self, request, format=None):
        data = request.data
        context_dict, currentCourse = initialContextDict(request)

        if data['type'] == 'create':
            if Channel.objects.filter(channel_name=data['channel_name'], course=currentCourse):
                return Response({'success': False, 'type':'name_error', 'reason': 'Channel already exists!'})
            if len(data['channel_topic']) > 40:
                return Response({'success': False, 'type':'topic_error', 'reason': 'Topic must be at most 40 characters!'})
            if not re.match(r'^[a-zA-Z\d\-_. ]+$', data['channel_name']):
                return Response({'success': False, 'type':'name_error', 'reason': 'Must contain only these special characters: underscores, hyphens, and periods'})

            user = User.objects.get(username=data['user']['username'], password=data['user']['password'], first_name=data['user']['first_name'], last_name=data['user']['last_name'], email=data['user']['email'])
            new_channel = Channel(channel_name=data['channel_name'], topic=data['channel_topic'], private=data['channel_private'], creator=user, course=currentCourse)
            new_channel.save()

            new_channel.users.add(user)
            new_channel.save()
                
            return Response({'success': True, 'channel_name': data['channel_name'], 'channel_url': new_channel.channel_url})
        elif data['type'] == 'change_topic':
            if len(data['channel_topic']) > 40:
                return Response({'success': False, 'type':'topic_error', 'reason': 'Topic must be at most 40 characters!'})

            channel = Channel.objects.get(channel_name=data['channel_name'], course=currentCourse)
            if channel.topic == data['channel_topic']:
                return Response({'success': False, 'type':'topic_error', 'reason': 'Please enter a topic!'})
            
            channel.topic = data['channel_topic']
            channel.save()
                
            return Response({'success': True, 'channel_name': data['channel_name'], 'channel_url': channel.channel_url})
        elif data['type'] == 'change_private_status':
            channel = Channel.objects.get(channel_name=data['channel_name'], course=currentCourse)
            channel.private = data['channel_private']
            channel.save()
            return Response({'success': True, 'channel_name': data['channel_name'], 'channel_url': channel.channel_url})
        elif data['type'] == 'add_users_to_channel':
            users_to_add = data['users']
            channel = Channel.objects.get(channel_name=data['channel_name'], course=currentCourse)
            added_users = []
            for user_id, add in users_to_add.items():
                user = User.objects.get(pk=int(user_id))
                if add:
                    added_users.append(user)
            
            updated = False
            for user in channel.users.all():
                if not user in added_users:
                    updated = True
                    break
            
            if updated:
                channel.users.set(added_users)
                channel.save()

                added_users = [UserSerializer(user).data for user in added_users]

                return Response({'success': True, 'channel_name': data['channel_name'], 'channel_url': channel.channel_url, 'added_users': added_users})
            else:
                return Response({'success': False, 'type': 'add_users_error', 'reason': 'Users are already in/out the room'})
        else:
            return Response({'success': False, 'type':'undefined', 'reason': 'Type must be stated'})
