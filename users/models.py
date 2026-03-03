from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. Email is unique and used as the primary
    identifier for notifications and invitations.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
