from Chat.models import Channel, Message
from Chat.serializers import  MessageSerializer, UserSerializer, CourseSerializer
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
import json

from Instructors.views.utils import initialContextDict
from Instructors.models import Courses

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.accept()
        # print(self.scope)
        context_dict, currentCourse = initialContextDict(None, self.scope['user'], self.scope['session'])

        channel_url = self.scope['url_route']['kwargs']['channel_url']
        self.room_name = Channel.objects.get(channel_url=channel_url, course=currentCourse).channel_name
        print('chat_%d_%s' % (currentCourse.courseID, self.room_name))
        self.room_group_name = 'chat_%d_%s' % (currentCourse.courseID, self.room_name.replace(" ", "_"))

        channels = Channel.objects.filter(course=currentCourse)
        self.groups.extend(['chat_%d_%s' % (currentCourse.courseID, channel.channel_name.replace(" ", "_")) for channel in channels])
        if not self.room_group_name in self.groups:
            self.groups.append(self.room_group_name)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        if channel_url == 'generic':
            user = UserSerializer(self.scope['user'])
            course_json = CourseSerializer(currentCourse)
            for group in self.groups:
                if not 'chat_%d_generic' %  currentCourse.courseID in group:
                    async_to_sync(self.channel_layer.group_send)(
                        group,
                        {
                            'type': 'broadcast',
                            'event': 'join_channel',
                            'channel_name': 'generic',
                            'user': user.data,
                            'course': course_json.data
                        }
                    )

        

    def disconnect(self, close_code):
        # Leave room group
        if self.room_group_name in self.groups:
            self.groups.remove(self.room_group_name)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['event']
        user_json = text_data_json['user']
        course_json = text_data_json['course']
        print(course_json)
        user = User.objects.get(username=user_json['username'], password=user_json['password'], first_name=user_json['first_name'], last_name=user_json['last_name'], email=user_json['email'])
        course = Courses.objects.get(courseID=course_json['courseID'])

        channel_name = self.room_name
        channel = Channel.objects.get(channel_name=channel_name, course=course)

        if message_type == 'message_channel':
            message = text_data_json['message']
            
            print("User: {}".format(user))
            print("Message: {}".format(message))
            print("Channel: {}".format(channel_name))

            
            message_obj = Message()
            message_obj.channel = channel
            message_obj.user = user
            message_obj.message = message
            message_obj.save()

            serializer = MessageSerializer(message_obj)
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'event': message_type,
                    'message': serializer.data,
                    'user': user_json,
                    'course': course_json,
                    'channel_name': channel_name
                }
            )
        elif message_type == 'join_channel':
            if not user in channel.users.all():
                channel.users.add(user)
                channel.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                        'channel_name': channel_name,
                        'user': user_json,
                        'course': course_json
                    }
                )
        elif message_type == 'change_topic':
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'event': message_type,
                    'channel_name': channel_name,
                    'user': user_json,
                    'course': course_json
                }
            )
        elif message_type == 'add_users_to_channel':
            added_users_json = text_data_json['added_users']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'broadcast',
                    'event': message_type,
                    'channel_name': channel_name,
                    'user': user_json,
                    'added_users': added_users_json,
                    'course': course_json
                }
            )
        elif message_type == 'leave_channel':
            if user in channel.users.all():
                channel.users.remove(user)
                channel.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                        'channel_name': channel_name,
                        'user': user_json,
                        'course': course_json
                    }
                )
        elif message_type == 'delete_channel':
            if channel.creator == user:
                for group in self.groups:
                    async_to_sync(self.channel_layer.group_send)(
                        group,
                        {
                            'type': 'broadcast',
                            'event': message_type,
                            'channel_name': channel_name,
                            'user': user_json,
                            'course': course_json
                        }
                    )
                self.groups.remove('chat_%d_%s' % (course.courseID, channel.channel_name.replace(" ", "_")))
                channel.delete()
        elif message_type == 'add_channel':
            channel_n = text_data_json['channel_name']
            
            print("Channel: {}".format(channel_n))
            print("Groups: {}".format(self.groups))
            for group in self.groups:
                async_to_sync(self.channel_layer.group_send)(
                    group,
                    {
                        'type': 'broadcast',
                        'event': message_type,
                        'channel_name': channel_name,
                        'user': user_json,
                        'course': course_json
                    }
                )

            if not 'chat_%d_%s' % (course.courseID, channel_n.replace(" ", "_")) in self.groups:
                self.groups.append('chat_%d_%s' % (course.courseID, channel_n.replace(" ", "_")))
        print(self.groups)

    # Receive message from room group
    def broadcast(self, event):
        # Send message to WebSocket
        self.send(text_data=json.dumps(event))
