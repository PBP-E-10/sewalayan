
from uuid import uuid4
from django.db import models


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(blank=False, null=False)

