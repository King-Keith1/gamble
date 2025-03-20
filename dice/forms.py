from django import forms

class RechargeForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1.00,
        label="Recharge Amount",
        widget=forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
    )