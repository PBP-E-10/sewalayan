from django.shortcuts import render
from item.models import Item


def design_page(request):
    return render(request, "design.html")

def landing_page(request):
    return render(request, "landing.html")