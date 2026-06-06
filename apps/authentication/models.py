from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('PO', 'Product Owner'),
        ('DEV', 'Developer'),
    ]
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    role = models.CharField(
        max_length=15,
        choices=ROLE_CHOICES,
        default='DEV'
    )

    def __str__(self):
        return self.email or self.username
