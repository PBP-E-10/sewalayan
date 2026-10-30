from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET

from order.models import Order


@require_GET
def get_order_json(request):
    is_buyer = request.GET.get("buyer", "True").lower() == "true"
    status = request.GET.get("status", "all").strip()

    orders = Order.objects.all()

    if is_buyer:
        orders = orders.filter(buyer=request.user)
    else:
        orders = orders.filter(item__owner=request.user)

    if status != 'all':
        orders = orders.filter(status=status)

    data = []
    for order in orders:
        data.append({
            "id": str(order.id),
            "fields": {
                "item_name": order.item.name,
                "item_id": order.item.id,
                "owner": order.item.owner.username,
                "buyer": order.buyer.username,
                "status": order.status_id,
                "purchase_price": str(order.purchase_price),
                "created_at": order.created_at.isoformat(),
                "taken_at": order.taken_at.isoformat(),
                "returned_at": order.returned_at.isoformat(),
            },
        })

    return JsonResponse(data, safe=False)


@require_POST
def decline_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    order = get_object_or_404(Order, id=order_id)

    if request.user != order.item.owner:
        return JsonResponse({'error': 'Halaman tidak ditemukan'}, status=404)
    if order.status != 'requested':
        return JsonResponse({'error': 'Order tidak dalam status pengajuan.'}, status=400)

    order.delete()
    # TODO: Notify the canceled order to the user

    return JsonResponse({'id': order.id}, status=201)


@require_POST
def accept_order(request, order_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Kamu harus login dulu.'}, status=401)

    order = get_object_or_404(Order, id=order_id)

    if request.user != order.item.owner:
        return JsonResponse({'error': 'Halaman tidak ditemukan'}, status=404)
    if order.status != 'requested':
        return JsonResponse({'error': 'Order tidak dalam status pengajuan.'}, status=400)

    order.status = 'accepted'
    order.save()

    item = order.item
    item.is_available = False
    item.save()

    # Semua permintaan order lain seharusnya ditolak
    other_orders = item.orders.filter(status='requested').exclude(id=order_id)

    for order in other_orders:
        order.delete()
        # TODO: Notify the canceled order to the user

    return JsonResponse({'id': order.id}, status=201)
