from django.shortcuts import render


def design_page(request):
    return render(request, "design.html")
