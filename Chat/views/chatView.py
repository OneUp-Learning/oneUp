from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.models import Channel
from Students.views.utils import studentInitialContextDict


@login_required
@ensure_csrf_cookie
def chatView(request):
    context_dict,currentCourse = studentInitialContextDict(request)
    channel, _ = Channel.objects.get_or_create(course=currentCourse, channel_name="generic")
    user = context_dict['student'].user
    if not Channel.objects.filter(course=currentCourse, channel_name="generic", users=user).exists():
        channel.users.add(user)
        channel.save()

    return render(request, 'Chat/chatApp.html', context_dict)