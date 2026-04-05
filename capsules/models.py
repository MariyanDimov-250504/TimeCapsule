from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator
from django.utils import timezone

User = get_user_model()


class Capsule(models.Model):
    PRIVACY_CHOICES = [
        ('private', 'Private - Only me'),
        ('shared', 'Shared - People I choose'),
        ('public', 'Public - Everyone'),
    ]

    STATUS_CHOICES = [
        ('sealed', 'Sealed'),
        ('opened', 'Opened'),
    ]

    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        help_text="Give your capsule a meaningful title"
    )
    description = models.TextField(
        blank=True,
        help_text="What memories are you preserving?"
    )

    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_capsules'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    open_date = models.DateTimeField(
        help_text="When should this capsule be opened? (Must be in the future)"
    )

    opened_at = models.DateTimeField(
        blank=True,
        null=True
    )

    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default='private'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='sealed'
    )

    allowed_users = models.ManyToManyField(
        User,
        blank=True,
        related_name='shared_capsules',
        help_text="Users who can view this capsule (if privacy is 'shared')"
    )

    cover_image = models.ImageField(
        upload_to='capsule_images/',
        blank=True,
        null=True
    )

    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('can_open_any_capsule', 'Can open any capsule regardless of date'),
        ]

    def __str__(self):
        return f"{self.title} - {self.creator.username}"

    def can_user_view(self, user):
        if user is None or not user.is_authenticated:
            return self.privacy == 'public'

        if user == self.creator:
            return True

        if self.privacy == 'public':
            return True

        if self.privacy == 'shared' and user in self.allowed_users.all():
            return True

        return False

    def can_user_open(self, user):
        if not self.can_user_view(user):
            return False

        if self.open_date > timezone.now():
            return False

        return True

    @property
    def is_openable(self):
        return self.open_date <= timezone.now() and self.status == 'sealed'

    @property
    def time_until_open(self):
        if self.open_date <= timezone.now():
            return "Ready to open!"

        delta = self.open_date - timezone.now()
        total_seconds = int(delta.total_seconds())

        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        if days > 0:
            return f"{days} day{'s' if days != 1 else ''} remaining"
        elif hours > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} remaining"
        elif minutes > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} remaining"
        else:
            return "Less than a minute remaining"

    @property
    def can_be_edited(self):
        return self.status == 'sealed'

class CapsuleContent(models.Model):
    CONTENT_TYPES = [
        ('text', 'Text Message'),
        ('image', 'Image'),
        ('memory', 'Memory Note'),
    ]

    capsule = models.ForeignKey(
        Capsule,
        on_delete=models.CASCADE,
        related_name='contents'
    )
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    title = models.CharField(max_length=100, blank=True)
    text_content = models.TextField(blank=True)
    image = models.ImageField(upload_to='capsule_contents/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.get_content_type_display()} in {self.capsule.title}"


class Report(models.Model):
    REPORT_REASONS = [
        ('inappropriate', 'Inappropriate Content'),
        ('sexual', 'Sexual Content'),
        ('illegal', 'Illegal Activity'),
        ('spam', 'Spam'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('dismissed', 'Dismissed'),
        ('action_taken', 'Action Taken'),
    ]

    capsule = models.ForeignKey(Capsule, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reason = models.CharField(max_length=20, choices=REPORT_REASONS)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_reports')

    def __str__(self):
        return f"Report on {self.capsule.title} by {self.reported_by.username}"
