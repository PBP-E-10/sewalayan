from django.http import HttpResponse

def show_item(data):
    return HttpResponse("Halo, ini halaman utama modul Item!")