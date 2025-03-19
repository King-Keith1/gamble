from django.db import models
from django.contrib.auth.models import User

class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    wager = models.DecimalField(max_digits=10, decimal_places=2)
    multiplier = models.IntegerField()  # e.g., 2, 3, 4, etc.
    guess = models.IntegerField()  # User's guessed number
    roll_result = models.IntegerField()  # Randomly generated roll
    won = models.BooleanField()  # True if user won, False if lost
    payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Winnings (or 0 if lost)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game by {self.user.username} at {self.timestamp}"