# Gamble/accounts/tests.py
from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSignalTests(TestCase):
    def test_profile_created_on_user_creation(self):
        """A UserProfile is automatically created when a new User is saved."""
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

    def test_profile_has_default_balance(self):
        """New profiles start with a $100 balance."""
        user = User.objects.create_user(username='balanceuser', password='testpass123')
        self.assertEqual(user.profile.balance, 100.00)

    def test_profile_not_duplicated_on_user_save(self):
        """Saving an existing user does not create a duplicate profile."""
        user = User.objects.create_user(username='saveuser', password='testpass123')
        user.first_name = 'Updated'
        user.save()
        self.assertEqual(UserProfile.objects.filter(user=user).count(), 1)

    def test_profile_str(self):
        """UserProfile __str__ returns the expected format."""
        user = User.objects.create_user(username='struser', password='testpass123')
        self.assertEqual(str(user.profile), "struser's Profile")


class SignupViewTests(TestCase):
    def test_signup_page_loads(self):
        response = self.client.get('/accounts/signup/')
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user_and_profile(self):
        response = self.client.post('/accounts/signup/', {
            'username': 'newplayer',
            'password1': 'SecurePass99!',
            'password2': 'SecurePass99!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        user = User.objects.get(username='newplayer')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())