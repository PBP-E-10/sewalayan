from django.shortcuts import render
from item.models import Category

CATEGORY_ICONS = {
    'elektronik': '🔌',
    'kamera-fotografi': '📷',
    'alat-outdoor': '⛺',
    'perlengkapan-pesta': '🎉',
    'alat-musik': '🎸',
    'perkakas': '🔧',
    'olahraga': '⚽',
}

def design_page(request):
    return render(request, "design.html")

def landing_page(request):
    categories = Category.objects.order_by('pk')
    for category in categories:
        category.icon = CATEGORY_ICONS.get(category.slug, '📦')
    return render(request, "landing.html", {'categories': categories})