from decimal import Decimal, InvalidOperation

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ItemForm
from .grading import calculate_condition_grade, is_eligible
from .models import Category, Item

LOGIN_URL = 'user:login'
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {'User-Agent': 'SewalayanApp/1.0 (student project)'}


# Helper 

def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def _parse_decimal(value):
    """Ubah teks harga jadi Decimal, atau None kalau kosong/tidak valid."""
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def geocode_address(address):
    """Kembalikan (lat, lon) dari Nominatim, atau (None, None) jika gagal."""
    if not address:
        return None, None
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={'q': address, 'format': 'json', 'limit': 1},
            headers=NOMINATIM_HEADERS,
            timeout=5,
        )
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
    return None, None


def _check_eligible(form, item):
    """Tolak barang yang gugur di syarat mutlak (knock-out) penilaian."""
    if not is_eligible(item):
        form.add_error(
            None,
            "Barang dengan kondisi ini tidak layak disewakan. "
            "Periksa kembali skor Keamanan, Fungsi, dan Kebersihan.",
        )
        return False
    return True


# ------------------------------------------------------------------ views ---

def item_list(request):
    categories = Category.objects.all()
    return render(request, 'item/item_list.html', {'categories': categories})


def get_items_json(request):
    query = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    grade = request.GET.get("grade", "").strip()
    location = request.GET.get("location", "").strip()
    min_price = _parse_decimal(request.GET.get("min_price", "").strip())
    max_price = _parse_decimal(request.GET.get("max_price", "").strip())

    items = Item.objects.select_related('category').order_by('-created_at')

    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category.isdigit():
        items = items.filter(category__id=int(category))
    if min_price is not None:
        items = items.filter(price_per_day__gte=min_price)
    if max_price is not None:
        items = items.filter(price_per_day__lte=max_price)
    if grade:
        items = items.filter(condition_grade__startswith=grade)
    if location:
        items = items.filter(location__icontains=location)

    data = []
    for item in items:
        data.append({
            "pk": str(item.pk),
            "fields": {
                "name": item.name,
                "description": item.description,
                "price_per_day": str(item.price_per_day),
                "condition_grade": item.condition_grade,
                "category_name": item.category.name if item.category else "",
                "location": item.location,
                "image": item.image.url if item.image else "",
            },
        })

    return JsonResponse(data, safe=False)


def item_detail(request, pk):
    item = get_object_or_404(Item.objects.select_related('owner', 'category'), pk=pk)
    return render(request, 'item/item_detail.html', {'item': item})


@login_required(login_url=LOGIN_URL)
def item_create(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user

            if _check_eligible(form, item):
                item.condition_grade = calculate_condition_grade(item)
                item.latitude, item.longitude = geocode_address(item.location)
                item.save()

                if _is_ajax(request):
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Barang berhasil disewakan dengan grade ' + item.condition_grade,
                    })
                return redirect('item:list')

        # Form tidak valid, atau barang gugur di syarat mutlak
        if _is_ajax(request):
            return JsonResponse({
                'status': 'error',
                'message': 'Validasi form gagal.',
                'errors': form.errors.get_json_data(),
            }, status=400)
    else:
        form = ItemForm()

    return render(request, 'item/item_form.html', {'form': form, 'action': 'Tambah'})


@login_required(login_url=LOGIN_URL)
def item_update(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.owner != request.user:
        return redirect('item:detail', pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            updated_item = form.save(commit=False)

            if _check_eligible(form, updated_item):
                updated_item.condition_grade = calculate_condition_grade(updated_item)
                # Geocode ulang hanya jika alamat berubah
                if 'location' in form.changed_data:
                    updated_item.latitude, updated_item.longitude = geocode_address(updated_item.location)
                updated_item.save()
                return redirect('item:detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)

    return render(request, 'item/item_form.html', {'form': form, 'action': 'Edit'})


@login_required(login_url=LOGIN_URL)
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if request.method == "POST" and item.owner == request.user:
        item.delete()
        messages.success(request, "Barang berhasil dihapus!")
        return redirect('item:list')

    return redirect('item:detail', pk=pk)