from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Profile

def profile_detail(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    return HttpResponse(f"Profil milik {profile.user.username}")