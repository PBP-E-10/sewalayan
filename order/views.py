from django.http import HttpResponse


def show_order(request):
    return HttpResponse("Ini bagian modul order!")
