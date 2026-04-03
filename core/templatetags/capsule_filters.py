from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.filter(name='time_until')
def time_until(date):
    if not date:
        return ""

    now = timezone.now()
    delta = date - now

    if delta.total_seconds() < 0:
        return "Opened"

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    seconds = delta.seconds % 60

    if days > 0:
        return f"{days} day{'s' if days != 1 else ''} left"
    elif hours > 0:
        return f"{hours} hour{'s' if hours != 1 else ''} left"
    elif minutes > 0:
        return f"{minutes} minute{'s' if minutes != 1 else ''} left"
    elif seconds > 0:
        return f"{seconds} second{'s' if seconds != 1 else ''} left"
    else:
        return "Opening now!"


@register.filter(name='capsule_status_icon')
def capsule_status_icon(status):
    icons = {
        'sealed': '🔒',
        'opened': '📖',
        'expired': '⏰',
    }
    return icons.get(status, '📦')


@register.filter(name='privacy_icon')
def privacy_icon(privacy):
    icons = {
        'private': '🔐',
        'shared': '👥',
        'public': '🌍',
    }
    return icons.get(privacy, '🔒')


@register.filter(name='truncate_chars')
def truncate_chars(value, max_length):
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'
