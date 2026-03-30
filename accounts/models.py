from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, max_length=500)

    def __str__(self):
        return self.username

    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True
    )

