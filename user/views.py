from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .forms import RegisterForm, LoginForm, ProfileForm
from .models import Profile


def show_user(request):
    return HttpResponse("Ini page user!")

@login_required(login_url="/user/login/")
def my_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    return redirect("user:profile_detail", profile_id=profile.id)

def profile_detail(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    is_owner = request.user.is_authenticated and profile.user == request.user
    return render(request, "user/profile_detail.html", {
        "profile": profile,
        "is_owner": is_owner,
    })

@login_required(login_url="/user/login/")
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("user:profile_detail", profile_id=profile.id)
    return render(request, "user/profile_edit.html", {"form": form})

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
        return redirect("item:list")
    return render(request, "user/login.html", {"form": form})

def logout_user(request):
    logout(request)
    return redirect("user:login")
