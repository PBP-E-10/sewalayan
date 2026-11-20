from django.urls import path

from .api_views import (
    accept_order,
    decline_order,
    finish_order,
    order_list,
    pay_order,
    pick_up_order,
)

app_name = "order_api"

urlpatterns =  [
    path("order/", order_list, name="list"),
    path("order/<uuid:order_id>/accept/", accept_order, name="accept"),
    path("order/<uuid:order_id>/decline/", decline_order, name="decline"),
    path("order/<uuid:order_id>/pay/", pay_order, name="pay"),
    path("order/<uuid:order_id>/pick-up/", pick_up_order, name="pick-up"),
    path("order/<uuid:order_id>/finish/", finish_order, name="finish"),
]
