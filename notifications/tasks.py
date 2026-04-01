from celery import shared_task
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


@shared_task
def send_capsule_ready_email(user_id, capsule_title, capsule_url):
    try:
        user = User.objects.get(id=user_id)
        subject = f'Your Time Capsule "{capsule_title}" is Ready to Open!'
        message = f"""
        Hello {user.username},

        Your time capsule "{capsule_title}" is now ready to be opened!

        Click here to open it: {capsule_url}

        Preserve your memories!
        TimeCapsule Team
        """
        send_mail(subject, message, 'noreply@timecapsule.com', [user.email])
        return f"Email sent to {user.email}"
    except Exception as e:
        return f"Error: {e}"


@shared_task
def send_capsule_shared_notification(user_id, owner_username, capsule_title, capsule_url):
    try:
        user = User.objects.get(id=user_id)
        subject = f'{owner_username} Shared a Time Capsule with You!'
        message = f"""
        Hello {user.username},

        {owner_username} has shared their time capsule "{capsule_title}" with you.

        View it here: {capsule_url}

        Preserve your memories!
        TimeCapsule Team
        """
        send_mail(subject, message, 'noreply@timecapsule.com', [user.email])
        return f"Email sent to {user.email}"
    except Exception as e:
        return f"Error: {e}"


@shared_task
def check_upcoming_openings():
    from capsules.models import Capsule

    today = timezone.now().date()
    upcoming_date = today + timedelta(days=7)

    upcoming_capsules = Capsule.objects.filter(
        open_date__date__gte=today,
        open_date__date__lte=upcoming_date,
        status='sealed'
    )

    count = 0
    for capsule in upcoming_capsules:
        try:
            subject = f'Reminder: Your Capsule "{capsule.title}" Opens Soon!'
            message = f"""
            Hello {capsule.creator.username},

            Your time capsule "{capsule.title}" will open on {capsule.open_date}.

            Only {capsule.days_until_open} days left!

            Preserve your memories!
            TimeCapsule Team
            """
            send_mail(subject, message, 'noreply@timecapsule.com', [capsule.creator.email])
            count += 1
        except Exception as e:
            print(f"Error sending to {capsule.creator.email}: {e}")

    return f"Sent reminders for {count} capsules"