from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm, LoginForm
from .models import Profile


def show_user(request):
    return HttpResponse("Ini page user!")

@login_required(login_url="/user/login/")
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return redirect("user:profile_detail", profile_id=profile.id)

def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
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
