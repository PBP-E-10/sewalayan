from django.urls import path
from item.views import show_item

item = (
    [ 
        path('', show_item, name='show_item'),
    ],
    'item'
)