from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='reviews_given', 
        null=True,
    )
    order = models.OneToOneField(
        'order.Order',
        on_delete=models.CASCADE,
        related_name='review',
        null=True,
    )
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer} - {self.rating}*"



class Report(models.Model):
    REASON_CHOICES = [
        ('damaged', 'Barang rusak / tidak sesuai deskripsi'),
        ('not_returned', 'Barang tidak dikembalikan'),
        ('late', 'Terlambat mengembalikan'),
        ('fraud', 'Penipuan'),
        ('other', 'Lainnya'),
    ]
    STATUS_CHOICES = [
        ('open', 'Baru'),
        ('in_review', 'Sedang ditinjau'),
        ('resolved', 'Selesai'),
        ('rejected', 'Ditolak'),
    ]

    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_made')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    admin_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Laporan {self.reporter} - {self.get_reason_display()}"

    @property
    def reported_user(self):
        if self.reporter_id == self.order.buyer_id:
            return self.order.item.owner
        return self.order.buyer