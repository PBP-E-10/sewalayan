from django.urls import path
from item import views

urlpatterns = [
    # Halaman utama katalog barang & pencarian
    path('', views.item_list, name='item_list'),

    # Halaman form tambah barang baru
    path('create/', views.item_create, name='item_create'),
    
    # Halaman detail barang berdasarkan Primary Key (pk/id)
    path('<int:pk>/', views.item_detail, name='item_detail'),
    
    # Halaman edit barang (hanya bisa diakses owner)
    path('<int:pk>/update/', views.item_update, name='item_update'),
    
    # Fungsi hapus barang (hanya bisa diakses owner)
    path('<int:pk>/delete/', views.item_delete, name='item_delete'),
]

