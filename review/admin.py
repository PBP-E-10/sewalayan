from django.contrib import admin
from review.models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'reviewer', 'item', 'rating', 'comment','created_at')
    list_filter = ('rating', 'item', 'created_at')
    search_fields = ('comment',)