# Gamble/dice/tests.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch

from .models import Game
from accounts.models import UserProfile


class DiceViewSetup(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='player', password='testpass123')
        self.profile = self.user.profile  # created via signal
        self.profile.balance = Decimal('100.00')
        self.profile.save()
        self.client.login(username='player', password='testpass123')


class IndexViewTests(DiceViewSetup):
    def test_index_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('dice:index'))
        self.assertRedirects(response, '/accounts/login/?next=/dice/')

    def test_index_loads_with_profile(self):
        response = self.client.get(reverse('dice:index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_profile', response.context)
        self.assertEqual(response.context['user_profile'].balance, Decimal('100.00'))

    def test_index_shows_recent_games(self):
        Game.objects.create(
            user=self.user, wager=10, multiplier=2, guess=1,
            roll_result=1, won=True, payout=20
        )
        response = self.client.get(reverse('dice:index'))
        self.assertEqual(len(response.context['games']), 1)


class PlayGameViewTests(DiceViewSetup):
    def _post(self, wager='10.00', multiplier='2', guess='1'):
        return self.client.post(reverse('dice:play_game'), {
            'wager': wager, 'multiplier': multiplier, 'guess': guess,
        })

    def test_get_redirects_to_index(self):
        response = self.client.get(reverse('dice:play_game'))
        self.assertRedirects(response, reverse('dice:index'))

    def test_win_updates_balance_correctly(self):
        with patch('dice.views.random.randint', return_value=1):
            self._post(wager='10.00', multiplier='2', guess='1')
        self.profile.refresh_from_db()
        # Deduct wager ($10), add payout ($20) → $110
        self.assertEqual(self.profile.balance, Decimal('110.00'))

    def test_loss_deducts_wager(self):
        with patch('dice.views.random.randint', return_value=2):
            self._post(wager='10.00', multiplier='2', guess='1')
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, Decimal('90.00'))

    def test_game_record_created(self):
        with patch('dice.views.random.randint', return_value=1):
            self._post(wager='10.00', multiplier='2', guess='1')
        self.assertEqual(Game.objects.filter(user=self.user).count(), 1)

    def test_wager_exceeding_balance_rejected(self):
        response = self._post(wager='999.00', multiplier='2', guess='1')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, Decimal('100.00'))  # unchanged

    def test_invalid_multiplier_rejected(self):
        response = self._post(multiplier='999')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_guess_out_of_range_rejected(self):
        response = self._post(multiplier='2', guess='5')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_non_numeric_wager_rejected(self):
        response = self._post(wager='abc')
        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)

    def test_win_shows_success_message(self):
        with patch('dice.views.random.randint', return_value=1):
            response = self._post(wager='10.00', multiplier='2', guess='1')
        self.assertRedirects(response, reverse('dice:index'))
        response = self.client.get(reverse('dice:index'))
        messages_list = list(response.context['messages'])
        self.assertTrue(any('guessed right' in str(m) for m in messages_list))


class RechargeViewTests(DiceViewSetup):
    def test_recharge_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('dice:recharge'))
        self.assertRedirects(response, '/accounts/login/?next=/dice/recharge/')

    def test_recharge_page_loads(self):
        response = self.client.get(reverse('dice:recharge'))
        self.assertEqual(response.status_code, 200)

    def test_valid_recharge_increases_balance(self):
        self.client.post(reverse('dice:recharge'), {'amount': '50.00'})
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, Decimal('150.00'))

    def test_recharge_below_minimum_rejected(self):
        response = self.client.post(reverse('dice:recharge'), {'amount': '0.50'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.balance, Decimal('100.00'))

    def test_recharge_redirects_to_index_on_success(self):
        response = self.client.post(reverse('dice:recharge'), {'amount': '20.00'})
        self.assertRedirects(response, reverse('dice:index'))