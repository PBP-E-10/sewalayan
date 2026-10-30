from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .grading import is_eligible


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    # Indikator Penilaian Objektif(skala 1-4)
    RATING_CHOICES = [
        (4, '4 - Sempurna / Optimal'),
        (3, '3 - Baik / Minor Saja'),
        (2, '2 - Cukup / Ada Penurunan Performa'),
        (1, '1 - Buruk / Gagal / Rusak Total'),
    ]
    functional_score = models.IntegerField(choices=RATING_CHOICES, default=4, verbose_name="Fungsi dan Performa")
    physical_score = models.IntegerField(choices=RATING_CHOICES, default=4, verbose_name="Kondisi Fisik")
    safety_score = models.IntegerField(choices=RATING_CHOICES, default=4, verbose_name="Keamanan Penggunaan")
    completeness_score = models.IntegerField(choices=RATING_CHOICES, default=4, verbose_name="Kelengkapan")
    hygiene_score = models.IntegerField(choices=RATING_CHOICES, default=4, verbose_name="Kebersihan dan Higienitas")

    # Hasil akhir skor yang hanya bisa diisi sistem
    condition_grade = models.CharField(max_length=50, blank=True, editable=False)

    # Status item berdasarkan ketersediaan & lokasi 
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Untuk insert gambar produk dan status waktu pembuatan
    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self):
        # Dipakai ModelForm dan admin: barang yang gugur syarat mutlak tidak lolos validasi
        if not is_eligible(self):
            raise ValidationError(
                "Barang dengan kondisi ini tidak layak disewakan. "
                "Periksa kembali skor Keamanan, Fungsi, dan Kebersihan."
            )

    @property
    def is_rented(self):
        return self.orders.filter(status__in=["accepted", "paid", "picked-up"]).exists()