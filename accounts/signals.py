# Gamble/accounts/signals.py
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile when a new User is created.
    For existing users, save the profile if it already exists.
    Uses get_or_create to safely handle cases where the profile
    may not exist yet (e.g. pre-existing users, fixture loading).
    """
    profile, _ = UserProfile.objects.get_or_create(user=instance)
    if not created:
        profile.save()