from django import template
from django.utils import timezone
from Instructors.views.utils import current_localtime, datetime_to_local

register = template.Library()

@register.filter
def passed_current_time(value):
    if value:
        print(f"DUE TEST: value: {datetime_to_local(value)} - now: {current_localtime()}")
        return current_localtime() >= datetime_to_local(value)
    
    return False

@register.filter
def raw_timestamp(value):
    return value

@register.filter
def get_value_indexed(l, i):
    try:
        return l[i]
    except:
        return None