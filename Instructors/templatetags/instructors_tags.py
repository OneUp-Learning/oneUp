from django import template
from Instructors.constants import  default_time_str

register = template.Library()

@register.filter
def default_date(value):
    if value.strftime("%m/%d/%Y %I:%M %p") == default_time_str:
        return ""
    return value
    