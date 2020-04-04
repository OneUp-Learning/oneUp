from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def passed_current_time(value):
    if value:
        print(f"DUE TEST: value: {timezone.localtime(value)} - now: {timezone.localtime(timezone.now())}")
        return timezone.localtime(timezone.now()) >= timezone.localtime(value)
    
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