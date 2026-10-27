import requests
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Item, Category
from decimal import Decimal, InvalidOperation
from .forms import ItemForm
from .models import Item
from .grading import calculate_condition_grade, is_eligible

LOGIN_URL = '/auth/login/'
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
NOMINATIM_HEADERS = {'User-Agent': 'SewalayanApp/1.0 (student project)'}


# Helper
def _is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def geocode_address(address):
    """Kembalikan (lat, lon) dari Nominatim, atau (None, None) jika gagal."""
    if not address:
        return None, None
    try:
        response = requests.get(
            NOMINATIM_URL,
            params={'q': address, 'format': 'json', 'limit': 1},
            headers=NOMINATIM_HEADERS,
            timeout=5,  # jangan biarkan request user menggantung
        )
        response.raise_for_status()
        results = response.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except (requests.RequestException, ValueError, KeyError, IndexError):
        pass
    return None, None

def _is_eligible(form, item):
    """Tolak barang yang gugur di syarat mutlak (knock-out) penilaian."""
    if not is_eligible(item):
        form.add_error(
            None,
            "Barang dengan kondisi ini tidak layak disewakan. "
            "Periksa kembali skor Keamanan, Fungsi, dan Kebersihan.",
        )
        return False
    return True

def _parse_decimal(value):
    """Ubah teks jadi Decimal, atau None kalau kosong/tidak valid."""
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None




def item_list(request):
    # Daftar kategori dikirim ke template untuk dropdown filter
    categories = Category.objects.order_by('name')
    return render(request, 'item/item_list.html', {'categories': categories})


def get_items_json(request):
    params = request.GET
    items = Item.objects.select_related('category').order_by('-created_at')

    # Pencarian teks
    query = params.get('q', '').strip()
    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Filter kategori (berdasarkan id)
    category = params.get('category', '').strip()
    if category.isdigit():
        items = items.filter(category_id=int(category))

    # Filter harga per hari
    min_price = _parse_decimal(params.get('min_price', ''))
    if min_price is not None:
        items = items.filter(price_per_day__gte=min_price)
    max_price = _parse_decimal(params.get('max_price', ''))
    if max_price is not None:
        items = items.filter(price_per_day__lte=max_price)

    # Filter kondisi: nilainya "Grade A", "Grade B", dst. (cocok dengan awal teks grade)
    grade = params.get('grade', '').strip()
    if grade:
        items = items.filter(condition_grade__startswith=grade)

    # Filter lokasi
    location = params.get('location', '').strip()
    if location:
        items = items.filter(location__icontains=location)

    data = [
        {
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
        }
        for item in items
    ]
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

            if _is_eligible(form, item):
                item.latitude, item.longitude = geocode_address(item.location)
                item.condition_grade = calculate_condition_grade(item)
                item.save()

                if _is_ajax(request):
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Barang berhasil disewakan dengan grade ' + item.condition_grade,
                    })
                return redirect('item_list')

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
        return redirect('item_detail', pk=pk)

    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            updated_item = form.save(commit=False)

            if _is_eligible(form, updated_item):
                # Geocode ulang hanya jika alamat berubah, supaya peta tidak menunjuk lokasi lama
                if 'location' in form.changed_data:
                    updated_item.latitude, updated_item.longitude = geocode_address(updated_item.location)
                updated_item.condition_grade = calculate_condition_grade(updated_item)
                updated_item.save()
                return redirect('item_detail', pk=item.pk)
    else:
        form = ItemForm(instance=item)

    return render(request, 'item/item_form.html', {'form': form, 'action': 'Edit'})


@login_required(login_url=LOGIN_URL)
@require_POST
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.owner == request.user:
        item.delete()
        return redirect('item_list')
    return redirect('item_detail', pk=pk)