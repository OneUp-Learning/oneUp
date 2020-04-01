from django import template
from Instructors.constants import  default_time_str
from django.utils import timezone

register = template.Library()

@register.filter
def default_date(value):
    if value.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") == default_time_str:
        return ""
    return value

@register.filter
def passed_current_time(value):
    if value.replace(microsecond=0).strftime("%m/%d/%Y %I:%M %p") == default_time_str:
        return False
    return timezone.now() >= value

@register.filter
def raw_timestamp(value):
    return value

@register.filter
def get_value_indexed(l, i):
    try:
        return l[i]
    except:
        return None