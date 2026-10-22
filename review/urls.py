from django.urls import path
from review.views import show_review, create_review, edit_review, delete_review


app_name = 'review'

urlpatterns = [
    path('', show_review, name='show'),
    path('create/', create_review, name='create'),
    path('<int:id>/edit/', edit_review, name='edit'),
    path('<int:id>/delete/', delete_review, name='delete'),
]
