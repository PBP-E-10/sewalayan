from django.urls import path
from .views import profile_detail, show_user

app_name = 'user'

urlpatterns = [
    path('<int:user_id>/', profile_detail, name='profile_detail'),
    path('', show_user, name='show')
]
