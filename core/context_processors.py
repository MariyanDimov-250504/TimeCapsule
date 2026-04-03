from capsules.models import Capsule
from django.contrib.auth import get_user_model

User = get_user_model()

def site_stats(request):
    return {
        'site_total_capsules': Capsule.objects.count(),
        'site_public_capsules': Capsule.objects.filter(privacy='public').count(),
        'site_total_users': User.objects.count(),
    }

def current_year(request):
    from django.utils import timezone
    return {
        'current_year': timezone.now().year,
    }
