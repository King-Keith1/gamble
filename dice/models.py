# Gamble/dice/models.py
from django.db import models
from django.contrib.auth.models import User

# The set of multipliers the game allows. Validated in the view and form
# so a tampered POST can't invent new values.
ALLOWED_MULTIPLIERS = (2, 3, 4, 5, 10)


class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    wager = models.DecimalField(max_digits=10, decimal_places=2)
    multiplier = models.IntegerField()
    guess = models.IntegerField()
    roll_result = models.IntegerField()
    won = models.BooleanField()
    payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Game by {self.user.username} at {self.timestamp}"