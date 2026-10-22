from django.http import HttpResponse
from django.shortcuts import render
from review.models import Review

def show_review(request):
    reviews = Review.objects.select_related('reviewer')
    context = {
        'reviews': reviews,
    }
    return render(request, 'review/review_list.html', context)