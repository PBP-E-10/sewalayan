from django.urls import path
from .views import (
    profile_detail, show_user, register, login_user,
    logout_user, my_profile, profile_edit,
)

app_name = 'user'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('me/', my_profile, name='me'),
    path('me/edit/', profile_edit, name='profile_edit'),
    path('<uuid:profile_id>/', profile_detail, name='profile_detail'),
    path('', show_user, name='show'),
]