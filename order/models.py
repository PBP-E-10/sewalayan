from uuid import uuid4
from django.db import models
from django.contrib.auth.models import User

from item.models import Item


def date_id_format(date):
    return date.strftime("%H:%M - %d/%m/%Y")


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, related_name='orders')
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='rents')

    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('paid', 'Paid'),
        ('picked-up', 'Picked-Up'),
        ('finished', 'Finished'),
    ]

    status = models.CharField(choices=STATUS_CHOICES, default='paid')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    taken_at = models.DateTimeField(blank=False, null=False)
    returned_at = models.DateTimeField(blank=False, null=False)

    @property
    def status_id(self):
        match self.status.lower():
            case 'requested':
                return 'Diajukan'
            case 'accepted':
                return 'Disetujui'
            case 'paid':
                return 'Terbayar'
            case 'picked-up':
                return 'Dipakai'
            case 'finished':
                return 'Selesai'

    @property
    def status_details(self):
        match self.status.lower():
            case 'requested':
                return 'Penyewaan diajukan, menunggu konfirmasi.'
            case 'accepted':
                return 'Penyewaan disetujui, menunggu pembayaran anda!'
            case 'paid':
                return 'Penyewaan terbayar, menunggu pengambilan barang.'
            case 'picked-up':
                return 'Barang dipakai, kembalikan tepat waktu ya!'
            case 'finished':
                return 'Penyewaan selesai.'

    @property
    def taken_at_fmt(self):
        return date_id_format(self.taken_at)

    @property
    def returned_at_fmt(self):
        return date_id_format(self.returned_at)
