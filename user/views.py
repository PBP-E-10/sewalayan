from django.contrib.auth import login, logout
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm, LoginForm
from .models import Profile


def show_user(request):
    return HttpResponse("Ini page user!")

def profile_detail(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    return HttpResponse(f"Profil milik {profile.user.username}")

def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user)
        return redirect("user:login")
    return render(request, "user/register.html", {"form": form})

def login_user(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("user:show")
    return render(request, "user/login.html", {"form": form})

def logout_user(request):
    logout(request)
    return redirect("user:login")