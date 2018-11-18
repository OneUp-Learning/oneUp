from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.models import Channel, Message
from Chat.serializers import ChannelSerializer, MessageSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
import json, re

class UserView(APIView):
    renderer_classes = (JSONRenderer, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        ''' Returns active signin user as json'''
        user = request.user

        user_serializer = UserSerializer(user)
        return Response(user_serializer.data)

class ChannelView(APIView):
    renderer_classes = (JSONRenderer, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Return a list of all channels.
        """
        channels = Channel.objects.all()
        user = request.user

        subscribed_channels = Channel.objects.filter(users=user)
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

        if data['type'] == 'create':
            # Validate new channel name
            if Channel.objects.filter(channel_name=data['channel_name']):
                return Response({'success': False, 'type':'name_error', 'reason': 'Channel already exists!'})
            if len(data['channel_topic']) > 40:
                return Response({'success': False, 'type':'topic_error', 'reason': 'Topic must be less than 41 characters!'})
            if not re.match(r'^[a-zA-Z\d\-_. ]+$', data['channel_name']):
                return Response({'success': False, 'type':'name_error', 'reason': 'Must contain only these special characters: underscores, hyphens, and periods'})

            # Create channel and set user as creator
            user = User.objects.get(username=data['user']['username'], password=data['user']['password'], first_name=data['user']['first_name'], last_name=data['user']['last_name'], email=data['user']['email'])
            new_channel = Channel(channel_name=data['channel_name'], topic=data['channel_topic'], creator=user)
            new_channel.save()
            # Add user to new created channel
            new_channel.users.add(user)
            new_channel.save()
                
            return Response({'success': True, 'channel_name': data['channel_name'], 'channel_url': new_channel.channel_url})
        elif data['type'] == 'change_topic':
            # Validate new topic
            if len(data['channel_topic']) > 40:
                return Response({'success': False, 'type':'topic_error', 'reason': 'Topic must be less than 41 characters!'})

            channel = Channel.objects.get(channel_name=data['channel_name'])
            if channel.topic == data['channel_topic']:
                return Response({'success': False, 'type':'topic_error', 'reason': 'Please enter a topic!'})
            
            # Set topic of channel
            channel.topic = data['channel_topic']
            channel.save()
                
            return Response({'success': True, 'channel_name': data['channel_name'], 'channel_url': channel.channel_url})
        else:
            return Response({'success': False, 'type':'undefined', 'reason': 'Type must be stated'})

class MessageView(APIView):
    renderer_classes = (JSONRenderer, )
    permission_classes = (IsAuthenticated,)

    def get(self, request, channel_url, format=None):
        """
        Return a list of all messages for a channel.
        """
        channel, _ = Channel.objects.get_or_create(channel_url=channel_url)
        # We want to show the last 25 messages, ordered most-recent-last
        messages = Message.objects.filter(channel=channel).order_by('-timestamp')
        paginator = Paginator(messages, 25)
        page = int(request.GET.get('page', 1))

        # Return no messages if we reached the end of the list of messages
        if page >= paginator.num_pages+1:
            return Response({})

        m = paginator.get_page(page)
    
        serializer = MessageSerializer(m, many=True)
        return Response(serializer.data)
