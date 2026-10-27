from django.urls import path
from item import views

urlpatterns = [
    # Halaman utama katalog barang & pencarian
    path('', views.item_list, name='item_list'),

    # Halaman form utuk tambah barang baru
    path('create/', views.item_create, name='item_create'),
    
    # Akses untuk lihat detail barang 
    path('<int:pk>/', views.item_detail, name='item_detail'),
    
    # Akses ke fitur edit barang (hanya bisa diakses owner)
    path('<int:pk>/update/', views.item_update, name='item_update'),
    
    # Akses ke fitur hapus barang (hanya bisa diakses owner)
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),

    path("api/items/", views.get_items_json, name="get_items_json")
]

