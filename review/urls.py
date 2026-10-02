from django.urls import path
from . import views

app_name = 'review'

urlpatterns = [
    path('item/<int:item_id>/', views.item_reviews, name='item_reviews'),
]