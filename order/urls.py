from django.urls import path
from order.views import create_order, show_order, show_order_details, show_rental, show_request

app_name = 'order'

urlpatterns = [
    path('', show_order, name="show"),
    path('rental', show_rental, name="rental"),
    path('request', show_request, name="request"),
    path('create/<int:item_id>', create_order, name="create"),
    path('details/<uuid:order_id>/', show_order_details, name="detail")
]
