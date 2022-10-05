from rest_framework import serializers
from django.contrib.auth.models import User
from Instructors.models import Courses

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name']
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Courses
        fields = ['courseID', 'courseName', 'courseDescription']
