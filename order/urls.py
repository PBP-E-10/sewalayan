from django.urls import include, path
from order.views import create_order, show_order, show_order_details, show_rental, show_request

from order.api import accept_order, decline_order, get_order_json, pay_order

app_name = 'order'

api = (
    [
        path("accept/<uuid:order_id>", accept_order, name="accept"),
        path("decline/<uuid:order_id>", decline_order, name="decline"),
        path("pay/<uuid:order_id>", pay_order, name="pay"),
        path("json", get_order_json, name="json"),
    ],
    "api"
)

urlpatterns = [
    path('', show_order, name="show"),
    path('api/', include(api)),
    path('rental', show_rental, name="rental"),
    path('request', show_request, name="request"),
    path('create/<int:item_id>', create_order, name="create"),
    path('details/<uuid:order_id>/', show_order_details, name="detail")
]
