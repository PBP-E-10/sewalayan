from django.urls import path
from . import api_views

app_name = "review_api"

urlpatterns = [
    path("reviews/", api_views.review_list, name="review-list"),
    path("reviews/<int:review_id>/", api_views.review_detail, name="review-detail"),
    path("reviews/order/<uuid:order_id>/", api_views.order_review, name="order-review"),

    path("reports/", api_views.report_list, name="report-list"),
    path("reports/<int:report_id>/", api_views.report_detail, name="report-detail"),
    path("reports/order/<uuid:order_id>/", api_views.order_report_create, name="order-report-create"),
]