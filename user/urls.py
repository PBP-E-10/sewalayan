from django.urls import path
from .views import profile_detail, show_user, register, login_user, logout_user

app_name = 'user'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('<int:user_id>/', profile_detail, name='profile_detail'),
    path('', show_user, name='show')
]
