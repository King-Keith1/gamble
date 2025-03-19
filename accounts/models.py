from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)  # Starting balance of $100

    def __str__(self):
        return f"{self.user.username}'s Profile"
