from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    # Label grade yang dipakai untuk barang yang tidak boleh disewakan
    NOT_ELIGIBLE_GRADE = "Tidak Layak Disewakan"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)

    # --- INDIKATOR PENILAIAN OBJEKTIF (Skala 1-4) ---
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

    # Hasil akhir grade otomatis dari sistem
    condition_grade = models.CharField(max_length=50, blank=True, editable=False)

    # Status ketersediaan & Lokasi (OpenStreetMap Nominatim)
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    image = models.ImageField(upload_to='item_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def calculate_condition_grade(self):
        """
        Aturan Keputusan (Decision Rules):
        - Keamanan <= 2 atau Fungsi == 1 atau Higienitas == 1 -> Tidak Layak Disewakan
        - Fungsi == 2                                          -> Grade D (Terbatas)
        - Semua indikator bernilai 4                           -> Grade A (Seperti Baru)
        - Fungsi & Keamanan 4, Fisik & Kelengkapan >= 3        -> Grade B (Sangat Baik)
        - Selebihnya                                           -> Grade C (Baik / Layak Pakai)
        """
        f = self.functional_score
        p = self.physical_score
        s = self.safety_score
        c = self.completeness_score
        h = self.hygiene_score

        if s <= 2 or f == 1 or h == 1:
            return self.NOT_ELIGIBLE_GRADE
        if f == 2:
            return "Grade D — Terbatas"
        if f == 4 and p == 4 and s == 4 and c == 4 and h == 4:
            return "Grade A — Seperti Baru"
        if f >= 4 and s >= 4 and p >= 3 and c >= 3:
            return "Grade B — Sangat Baik"
        return "Grade C — Baik/Layak Pakai"

    def save(self, *args, **kwargs):
        # Grade selalu dihitung ulang, termasuk saat barang dibuat lewat admin/shell
        self.condition_grade = self.calculate_condition_grade()
        super().save(*args, **kwargs)