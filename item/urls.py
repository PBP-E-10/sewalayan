from django.urls import path
from item.views import show_item

app_name = 'item'

urlpatterns = [
    path('', show_item, name='show'),
]
