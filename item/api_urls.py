from django.urls import path
from . import api_views

app_name = "item_api"

urlpatterns = [
    path("items/", api_views.item_list, name="item-list"),
    path("items/<int:item_id>/", api_views.item_detail, name="item-detail"),
]