from django.urls import path
from order.views import show_order, show_order_details, show_rental, show_request

app_name = 'order'

urlpatterns = [
    path('', show_order, name="show"),
    path('rental', show_rental, name="rental"),
    path('details/<uuid:order_id>/', show_order_details, name="detail")
]
