from django.http import HttpResponse


def show_review(request):
    return HttpResponse("Hi ini page review")