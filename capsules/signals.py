from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Capsule
from notifications.tasks import send_capsule_shared_notification
from notifications.models import Notification

@receiver(post_save, sender=Capsule)
def check_capsule_ready(sender, instance, created, **kwargs):
    if not created and instance.status == 'opened':
        Notification.objects.create(
            user=instance.creator,
            notification_type='capsule_ready',
            title=f'Capsule "{instance.title}" Opened',
            message=f'Your time capsule was opened on {instance.opened_at}',
            link=f'/capsules/{instance.id}/'
        )

@receiver(m2m_changed, sender=Capsule.allowed_users.through)
def capsule_shared(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Send notification when capsule is shared with new users"""
    if action == 'post_add':
        for user_id in pk_set:
            Notification.objects.create(
                user_id=user_id,
                notification_type='capsule_shared',
                title=f'Capsule "{instance.title}" Shared With You',
                message=f'{instance.creator.username} shared their time capsule with you.',
                link=f'/capsules/{instance.id}/'
            )
            send_capsule_shared_notification.delay(
                user_id,
                instance.creator.username,
                instance.title,
                f'/capsules/{instance.id}/'
            )
