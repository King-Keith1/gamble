from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Game
from accounts.models import UserProfile
from .forms import RechargeForm  # Import the new form
from decimal import Decimal
import random

@login_required
def index(request):
    user_profile = request.user.userprofile
    games = Game.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, 'dice/index.html', {'user_profile': user_profile, 'games': games})

@login_required
def play_game(request):
    if request.method == 'POST':
        user_profile = request.user.userprofile
        wager = Decimal(request.POST.get('wager'))
        multiplier = int(request.POST.get('multiplier'))
        guess = int(request.POST.get('guess'))

        if wager <= 0 or wager > user_profile.balance:
            return render(request, 'dice/index.html', {
                'user_profile': user_profile,
                'games': Game.objects.filter(user=request.user).order_by('-timestamp')[:10],
                'error': 'Invalid wager amount.'
            })

        if guess < 1 or guess > multiplier:
            return render(request, 'dice/index.html', {
                'user_profile': user_profile,
                'games': Game.objects.filter(user=request.user).order_by('-timestamp')[:10],
                'error': f'Guess must be between 1 and {multiplier}.'
            })

        roll_result = random.randint(1, multiplier)
        won = (guess == roll_result)
        payout = wager * Decimal(multiplier) if won else Decimal('0.00')

        user_profile.balance -= wager
        if won:
            user_profile.balance += payout
        user_profile.save()

        game = Game(
            user=request.user,
            wager=wager,
            multiplier=multiplier,
            guess=guess,
            roll_result=roll_result,
            won=won,
            payout=payout
        )
        game.save()

        return redirect('dice:index')

    return redirect('dice:index')

@login_required
def recharge(request):
    if request.method == 'POST':
        form = RechargeForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            user_profile = request.user.userprofile
            user_profile.balance += amount
            user_profile.save()
            messages.success(request, f'Successfully recharged ${amount:.2f}! Your new balance is ${user_profile.balance:.2f}.')
            return redirect('dice:index')
    else:
        form = RechargeForm()
    return render(request, 'dice/recharge.html', {'form': form})