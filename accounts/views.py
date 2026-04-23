# Gamble/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django import forms


class SignupForm(UserCreationForm):
    """
    Extends the built-in UserCreationForm to include an optional email field.
    Using a custom form also makes it easy to add fields later (avatar, etc.)
    without touching the view.
    """
    email = forms.EmailField(
        required=False,
        help_text='Optional. Used for account recovery.',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2')


SIGNUP_REDIRECT = reverse_lazy('dice:index')
ALREADY_LOGGED_IN_REDIRECT = reverse_lazy('dice:index')


def signup(request):
    # Redirect already-authenticated users away from the signup page.
    if request.user.is_authenticated:
        return redirect(ALREADY_LOGGED_IN_REDIRECT)

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request,
                user,
                # Explicitly specify the backend so Django doesn't raise
                # ValueError if multiple auth backends are ever configured.
                backend='django.contrib.auth.backends.ModelBackend',
            )
            return redirect(SIGNUP_REDIRECT)
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})