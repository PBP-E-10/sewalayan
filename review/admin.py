from django.contrib import admin
from review.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'rating', 'comment','created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment',)