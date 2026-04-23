"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
 
urlpatterns = [
    path('admin/', admin.site.urls),
 
    # Accounts: login, logout, signup
    path('accounts/', include('accounts.urls')),
 
    # Dice game
    path('dice/', include('dice.urls')),
 
    # Fixed: previously dice.urls was included twice (at '' AND 'dice/').
    # That causes an app_name namespace collision and makes {% url 'dice:index' %}
    # resolve ambiguously. Replaced with a simple redirect so '/' goes to the game.
    path('', RedirectView.as_view(url='/dice/', permanent=False)),
]
 
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
 