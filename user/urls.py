from django.urls import path
from . import views

user = (
    [
        path('<int:user_id>/', views.profile_detail, name='profile_detail'),
    ],
    'user'
)