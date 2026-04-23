# Gamble/dice/forms.py
from django import forms
from .models import ALLOWED_MULTIPLIERS


class RechargeForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1.00,
        label="Recharge Amount",
        widget=forms.NumberInput(attrs={
            'step': '0.01',
            'class': 'form-control',
            'placeholder': '0.00',
        }),
    )


class PlayGameForm(forms.Form):
    """
    Validates all play_game POST fields server-side so the view
    never touches raw POST strings directly.
    """
    MULTIPLIER_CHOICES = [(m, f"{m}×") for m in ALLOWED_MULTIPLIERS]

    wager = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
    )
    multiplier = forms.TypedChoiceField(
        choices=MULTIPLIER_CHOICES,
        coerce=int,
    )
    guess = forms.IntegerField(min_value=1)

    def clean(self):
        cleaned = super().clean()
        multiplier = cleaned.get('multiplier')
        guess = cleaned.get('guess')
        if multiplier and guess and guess > multiplier:
            raise forms.ValidationError(
                f"Guess must be between 1 and {multiplier}."
            )
        return cleaned