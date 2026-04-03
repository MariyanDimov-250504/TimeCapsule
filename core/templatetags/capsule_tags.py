from django import template
from django.db.models import Count, Sum
from capsules.models import Capsule
from django.contrib.auth import get_user_model

User = get_user_model()
register = template.Library()

@register.simple_tag
def total_capsules_count():
    return Capsule.objects.count()

@register.simple_tag
def public_capsules_count():
    return Capsule.objects.filter(privacy='public').count()

@register.simple_tag
def total_users_count():
    return User.objects.count()

@register.simple_tag
def total_views_count():
    return Capsule.objects.aggregate(total=Sum('views_count'))['total'] or 0

@register.simple_tag
def recent_capsules(limit=5):
    return Capsule.objects.filter(privacy='public')[:limit]

@register.inclusion_tag('includes/capsule_card.html')
def capsule_card(capsule, show_actions=True):
    return {
        'capsule': capsule,
        'show_actions': show_actions,
    }

@register.inclusion_tag('includes/pagination.html')
def pagination(page_obj, request):
    return {
        'page_obj': page_obj,
        'request': request,
    }
