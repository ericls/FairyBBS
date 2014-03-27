__author__ = 'TianShuo'
from django import template
from fairy import settings
from fairy import conf

register = template.Library()


'''
usage:
first
    {% load settingsvalue %}
then
   {% settings_value "MAX_UPLOAD_SIZE" %}
   or
    {% settings_value "logoname" %}

'''

@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")

@register.simple_tag
def conf_value(name):
    return getattr(conf, name, "")



