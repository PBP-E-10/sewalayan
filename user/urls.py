from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('<int:user_id>/', views.profile_detail, name='profile_detail'),
]