from rest_framework import serializers
from django.contrib.auth.models import User
from Chat.models import Channel, Message
from Instructors.models import Courses


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ['courseID', 'courseName', 'courseDescription']

class ChannelSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    users = UserSerializer(read_only=True, many=True)
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Channel
        fields = ['course', 'channel_name', 'channel_url', 'topic', 'users', 'creator']

class MessageSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer()
    user = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'channel', 'user', 'message', 'timestamp']


