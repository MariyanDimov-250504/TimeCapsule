from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinLengthValidator, MinValueValidator
from django.utils import timezone
from datetime import date

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
        ('expired', 'Expired'),
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

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.open_date and not self.opened_at:
            if self.open_date <= timezone.now():
                self.status = 'expired'
        super().save(*args, **kwargs)

    def can_user_view(self, user):
        if not user.is_authenticated:
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

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=['views_count'])

    @property
    def is_openable(self):
        from django.utils import timezone
        return self.open_date <= timezone.now() and self.status == 'sealed'

    @property
    def days_until_open(self):
        from django.utils import timezone
        if self.open_date > timezone.now():
            delta = self.open_date - timezone.now()
            return delta.days
        return 0

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
