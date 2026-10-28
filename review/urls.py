from django.urls import path
from review.views import (
    show_review, review_order,
    show_review_json, delete_review_ajax,
    show_item_reviews,
)

app_name = 'review'

urlpatterns = [
    path('', show_review, name='show'),
    path('json/', show_review_json, name='show_json'),
    path('order/<uuid:order_id>/', review_order, name='order_review'),
    path('<int:id>/delete-ajax/', delete_review_ajax, name='delete_ajax'),
    path('item/<int:item_id>/', show_item_reviews, name='item_reviews'),
]