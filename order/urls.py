
from django.urls import path
from order.views import show_order

order = (
    [
        path('', show_order, name="show"),
    ],
    'order'
)
