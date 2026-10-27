from django.urls import path
from review.views import (
    show_review, edit_review,
    show_review_json, create_review_ajax, delete_review_ajax,
    show_item_reviews, create_report_ajax, show_my_reports,
)

app_name = 'review'

urlpatterns = [
    path('', show_review, name='show'),
    path('<int:id>/edit/', edit_review, name='edit'),
    path('json/', show_review_json, name='show_json'),
    path('order/<uuid:order_id>/create-ajax/', create_review_ajax, name='create_ajax'),
    path('<int:id>/delete-ajax/', delete_review_ajax, name='delete_ajax'),
    path('item/<int:item_id>/', show_item_reviews, name='item_reviews'),

    path('report/', show_my_reports, name='my_reports'),
    path('report/order/<uuid:order_id>/create-ajax/', create_report_ajax, name='create_report_ajax'),
]