from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'sewalayan'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review #{self.pk} - {self.rating}*"