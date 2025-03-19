from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dice:index')
        else:
            # Print form errors to the console for debugging
            print("Form errors:", form.errors)
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})