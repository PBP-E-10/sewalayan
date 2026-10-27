from django.shortcuts import render
from item.models import Item


def design_page(request):
    return render(request, "design.html")

def landing_page(request):
    latest_items = Item.objects.order_by('-created_at')[:6]
    context = {
        'latest_items': latest_items,
    }
    return render(request, "landing.html", context)