from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from Chat.models import Channel


@login_required
@ensure_csrf_cookie
def chatView(request):
    channel, _ = Channel.objects.get_or_create(channel_name="generic")
    user = request.user
    if not Channel.objects.filter(channel_name="generic", users=user).exists():
        channel.users.add(user)
        channel.save()

    return render(request, 'Chat/chatApp.html')