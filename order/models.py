from uuid import uuid4
from django.db import models

from item.models import Item
from user.models import Profile


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='rents')

    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    taken_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(blank=False, null=False)

