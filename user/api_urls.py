from django.urls import path

from . import api_views

app_name = "user_api"

urlpatterns = [
    path("register/", api_views.register_api, name="register"),
    path("login/", api_views.login_api, name="login"),
    path("logout/", api_views.logout_api, name="logout"),
    path("me/", api_views.me_api, name="me"),
    path("<uuid:profile_id>/", api_views.profile_detail_api, name="profile-detail"),
]

