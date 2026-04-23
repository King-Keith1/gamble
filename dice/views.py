# Gamble/dice/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .models import Game
from accounts.models import UserProfile
from .forms import RechargeForm, PlayGameForm
from decimal import Decimal
import random


def _get_recent_games(user):
    return Game.objects.filter(user=user).order_by('-timestamp')[:10]


@login_required
def index(request):
    # Fixed: was request.user.userprofile — related_name is now 'profile'
    user_profile = request.user.profile
    games = _get_recent_games(request.user)
    return render(request, 'dice/index.html', {
        'user_profile': user_profile,
        'games': games,
    })


@login_required
def play_game(request):
    if request.method != 'POST':
        return redirect('dice:index')

    form = PlayGameForm(request.POST)

    if not form.is_valid():
        # Fixed: raw POST values previously raised unhandled exceptions on bad input.
        # Now we re-render with the first form error as a user-facing message.
        error = next(iter(form.errors.values()))[0]
        user_profile = request.user.profile
        return render(request, 'dice/index.html', {
            'user_profile': user_profile,
            'games': _get_recent_games(request.user),
            'error': error,
        })

    wager = form.cleaned_data['wager']
    multiplier = form.cleaned_data['multiplier']
    guess = form.cleaned_data['guess']

    # Fixed: select_for_update() + atomic block prevents a race condition where
    # two simultaneous POSTs both read the same balance, both pass the wager
    # check, and both deduct — leaving the balance negative.
    try:
        with transaction.atomic():
            user_profile = UserProfile.objects.select_for_update().get(
                user=request.user
            )

            if wager > user_profile.balance:
                return render(request, 'dice/index.html', {
                    'user_profile': user_profile,
                    'games': _get_recent_games(request.user),
                    'error': 'Wager exceeds your current balance.',
                })

            roll_result = random.randint(1, multiplier)
            won = (guess == roll_result)
            payout = wager * Decimal(multiplier) if won else Decimal('0.00')

            user_profile.balance -= wager
            if won:
                user_profile.balance += payout

            # Fixed: both saves are inside the same transaction — if either fails,
            # neither is committed, keeping the DB consistent.
            user_profile.save()
            Game.objects.create(
                user=request.user,
                wager=wager,
                multiplier=multiplier,
                guess=guess,
                roll_result=roll_result,
                won=won,
                payout=payout,
            )

    except UserProfile.DoesNotExist:
        messages.error(request, 'User profile not found. Please contact support.')
        return redirect('dice:index')

    # Fixed: previously redirected silently with no outcome feedback.
    if won:
        messages.success(
            request,
            f'🎲 Rolled {roll_result} — you guessed right! Payout: ${payout:.2f}. '
            f'New balance: ${user_profile.balance:.2f}.'
        )
    else:
        messages.error(
            request,
            f'🎲 Rolled {roll_result} — you guessed {guess}. Better luck next time! '
            f'New balance: ${user_profile.balance:.2f}.'
        )

    return redirect('dice:index')


@login_required
def recharge(request):
    if request.method == 'POST':
        form = RechargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            # Fixed: was request.user.userprofile — related_name is now 'profile'
            with transaction.atomic():
                user_profile = UserProfile.objects.select_for_update().get(
                    user=request.user
                )
                user_profile.balance += amount
                user_profile.save()
            messages.success(
                request,
                f'Successfully recharged ${amount:.2f}! '
                f'New balance: ${user_profile.balance:.2f}.'
            )
            return redirect('dice:index')
    else:
        form = RechargeForm()

    return render(request, 'dice/recharge.html', {'form': form})