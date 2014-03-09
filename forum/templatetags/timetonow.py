#encoding=utf-8
from __future__ import unicode_literals
from datetime import date, datetime

from django import template
from django.template import defaultfilters
from django.utils.translation import pgettext, ungettext, ugettext as _
from django.utils.timezone import is_aware, utc

register = template.Library()


@register.filter
def time_to_now(value):
    """
    For date and time values shows how many seconds, minutes or hours ago
    compared to current timestamp returns representing string.
    """
    if not isinstance(value, date):  # datetime is a subclass of date
        return value

    now = datetime.now(utc if is_aware(value) else None)
    if value < now:
        delta = now - value
        if delta.days != 0:
            return str(delta.days) + '天前'
        elif delta.seconds == 0:
            return '刚刚'
        elif delta.seconds < 60:
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                '一秒前', '%(count)s\u00a0秒前', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                '一分钟前', '%(count)s\u00a0分钟前', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                '一个小时前', '%(count)s\u00a0小时前', count
            ) % {'count': count}
    else:
        delta = value - now
        if delta.days != 0:
            return pgettext(
                'naturaltime', '%(delta)s from now'
            ) % {'delta': defaultfilters.timeuntil(value, now)}
        elif delta.seconds == 0:
            return _('now')
        elif delta.seconds < 60:
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'a second from now', '%(count)s\u00a0seconds from now', delta.seconds
            ) % {'count': delta.seconds}
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'a minute from now', '%(count)s\u00a0minutes from now', count
            ) % {'count': count}
        else:
            count = delta.seconds // 60 // 60
            return ungettext(
                # Translators: \\u00a0 is non-breaking space
                'an hour from now', '%(count)s\u00a0hours from now', count
            ) % {'count': count}
