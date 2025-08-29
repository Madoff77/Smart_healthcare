from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login

from .forms import PatientSignUpForm


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Compte créé. Vous pouvez vous connecter.")
            return redirect('login')  # django.contrib.auth.views.LoginView name par défaut
    else:
        form = PatientSignUpForm()
    return render(request, 'registration/signup.html', {"form": form})