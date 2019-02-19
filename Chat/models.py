from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from Instructors.models import Courses
from django.template.defaultfilters import slugify
import random
# Create your models here.
class Channel(models.Model):
    channel_name = models.TextField()
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name="the related course", db_index=True)
    channel_url = models.SlugField(null=True, blank=True)
    topic = models.TextField(max_length=40, blank=True, null=True)
    private = models.BooleanField(default=False) 
    users = models.ManyToManyField(User, blank=True, related_name='subscribers')
    creator = models.ForeignKey(User, null=True, blank=True, related_name='creator', on_delete=models.CASCADE)
    
    class Meta():
        unique_together = ('channel_name', 'course', 'channel_url')

    def __str__(self):
        return "Channel ID: {} - Course: {} - Slug: {} - Topic: {} - Private: {} - Users: {} - Creator: {}".format(self.channel_name, self.course, self.channel_url, self.topic, self.private, self.users, self.creator)

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.channel_url = slugify(self.channel_name)

        super(Channel, self).save(*args, **kwargs)

class Message(models.Model):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    def __str__(self):
        return "Channel: {} - User: {} - Timestamp: {} - Message: {}".format(self.channel, self.user, self.timestamp, self.message)