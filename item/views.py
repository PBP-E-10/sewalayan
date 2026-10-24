from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from models import Item, Category
from forms import ItemForm
import requests

def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user # User harus login
            
            # INTEGRASI PUBLIC API OPENSTREETMAP (NOMINATIM) 
            address = item.location
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {'q': address, 'format': 'json', 'limit': 1}
            headers = {'User-Agent': 'SewalayanApp/1.0 (student project)'}
            
            try:
                response = requests.get(nominatim_url, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        item.latitude = float(data[0]['lat'])
                        item.longitude = float(data[0]['lon'])
            except Exception as e:
                # Kalau koneksi API gagal, biarkan lat/lon kosong agar tidak bikin error 500
                pass
            
            item.save()
            return redirect('item:item_list')
    else:
        form = ItemForm()
    
    return render(request, 'item/item_form.html', {'form': form})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    return render(request, 'item/item_detail.html', {'item': item})

@login_required(login_url='/auth/login/')
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save()
            return redirect('item:item_list')
    else:
        form = ItemForm()
    return render(request, 'item/item_form.html', {'form': form, 'action': 'Tambah'})

@login_required(login_url='/auth/login/')
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    # Validasi owner yg boleh edit
    if item.owner != request.user:
        return redirect('item:item_list')
        
    if request.method == 'POST':
        # Menerima request.method FILES jika ada input gambar
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item:item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)
    return render(request, 'item/item_form.html', {'form': form, 'action': 'Edit'})

@login_required(login_url='/auth/login/')
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    # Validasi owner
    if item.owner == request.user:
        item.delete()
    return redirect('item:item_list')