from rest_framework import serializers
from django.contrib.auth.models import User
from Chat.models import Channel, Message
from Instructors.models import Courses

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ['courseID', 'courseName', 'courseDescription']

class ChannelSerializer(serializers.ModelSerializer):
    course = CourseSerializer()
    users = UserSerializer(read_only=True, many=True)
    creator = UserSerializer(read_only=True)
    class Meta:
        model = Channel
        fields = ['channel_name', 'course', 'channel_url', 'topic', 'private', 'users', 'creator']

class MessageSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer()
    user = UserSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'channel', 'user', 'message', 'timestamp']


