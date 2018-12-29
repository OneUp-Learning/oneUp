from django import template
from Instructors.constants import  default_time_str
from django.utils import timezone

register = template.Library()

@register.filter
def default_date(value):
    if value.strftime("%m/%d/%Y %I:%M %p") == default_time_str:
        return ""
    return value

@register.filter
def passed_current_time(value):
    if value.strftime("%m/%d/%Y %I:%M %p") == default_time_str:
        return False
    return timezone.now() >= value

    