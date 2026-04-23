# Gamble/dice/admin.py
from django.contrib import admin
from .models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('user', 'wager', 'multiplier', 'guess', 'roll_result', 'won', 'payout', 'timestamp')
    list_filter = ('won', 'multiplier')
    search_fields = ('user__username',)
    ordering = ('-timestamp',)