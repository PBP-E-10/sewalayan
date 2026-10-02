from django.urls import path
from review.views import show_review

review = (
    [
        path('', show_review, name="show"),
    ],
    'review',
)