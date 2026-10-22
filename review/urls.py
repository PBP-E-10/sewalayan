from django.urls import path
from review.views import show_review, create_review

app_name = 'review'

urlpatterns = [
    path('', show_review, name='show'),
    path('create/', create_review, name='create'),
]
