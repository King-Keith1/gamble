from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Game
from accounts.models import UserProfile
from decimal import Decimal  # Import Decimal
import random

@login_required
def index(request):
    # Get or create the user's profile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    games = Game.objects.filter(user=request.user).order_by('-timestamp')[:10]  # Last 10 games
    return render(request, 'dice/index.html', {'user_profile': user_profile, 'games': games})

@login_required
def play_game(request):
    if request.method == 'POST':
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        wager = Decimal(request.POST.get('wager'))  # Convert wager to Decimal
        multiplier = int(request.POST.get('multiplier'))
        guess = int(request.POST.get('guess'))

        # Validate wager
        if wager <= 0 or wager > user_profile.balance:
            return render(request, 'dice/index.html', {
                'user_profile': user_profile,
                'games': Game.objects.filter(user=request.user).order_by('-timestamp')[:10],
                'error': 'Invalid wager amount.'
            })

        # Validate guess
        if guess < 1 or guess > multiplier:
            return render(request, 'dice/index.html', {
                'user_profile': user_profile,
                'games': Game.objects.filter(user=request.user).order_by('-timestamp')[:10],
                'error': f'Guess must be between 1 and {multiplier}.'
            })

        # Generate random roll (1 to multiplier)
        roll_result = random.randint(1, multiplier)

        # Determine if the user won
        won = (guess == roll_result)
        payout = wager * Decimal(multiplier) if won else Decimal('0.00')  # Ensure payout is a Decimal

        # Update user balance
        user_profile.balance -= wager
        if won:
            user_profile.balance += payout
        user_profile.save()

        # Save the game
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