# Gamble/accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Explicitly named so {% url 'accounts:login' %} and 'accounts:logout' resolve correctly.
    # Do NOT use include('django.contrib.auth.urls') here — that registers names under
    # the 'auth' namespace, which conflicts with the 'accounts' namespace used in templates.
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(template_name='registration/logged_out.html'),
        name='logout',
    ),
    path('signup/', views.signup, name='signup'),
]