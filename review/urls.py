from django.urls import path
from review.views import (
    show_review, create_review, edit_review, delete_review,
    show_review_json, create_review_ajax, delete_review_ajax,
)

app_name = 'review'

urlpatterns = [
    path('', show_review, name='show'),
    path('create/', create_review, name='create'),
    path('<int:id>/edit/', edit_review, name='edit'),
    path('<int:id>/delete/', delete_review, name='delete'),
    path('json/', show_review_json, name='show_json'),
    path('create-ajax/', create_review_ajax, name='create_ajax'),
    path('<int:id>/delete-ajax/', delete_review_ajax, name='delete_ajax'),
]