from django.http import HttpResponse
from .models import Review


def item_reviews(request, item_id):
    reviews = Review.objects.filter(item_id=item_id)
    return HttpResponse(f"Ada {reviews.count()} ulasan untuk item {item_id}")