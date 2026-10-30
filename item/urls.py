from django.urls import path

from . import views

app_name = 'item'

urlpatterns = [
    # Halaman utama katalog barang & pencarian
    path('', views.item_list, name='list'),
    # Halaman form untuk tambah barang baru
    path('create/', views.item_create, name='create'),

    # Akses untuk lihat detail barang
    path('<int:pk>/', views.item_detail, name='detail'),

    # Akses ke fitur edit barang (hanya bisa diakses owner)
    path('<int:pk>/update/', views.item_update, name='update'),

    # Akses ke fitur hapus barang (hanya bisa diakses owner)
    path('<int:pk>/delete/', views.item_delete, name='delete'),

    path("api/items/", views.get_items_json, name="get_json"),
]