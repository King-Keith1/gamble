# Gamble/accounts/models.py
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',  # Use user.profile instead of user.userprofile
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=100.00,
    )

    def __str__(self):
        return f"{self.user.username}'s Profile"