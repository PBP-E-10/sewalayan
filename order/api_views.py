from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer

AUTH = [TokenAuthentication, SessionAuthentication]

def _serialize(order, request):
    return OrderSerializer(order, context={"request": request}).data


def _forbidden(message):
    return Response({"detail": message}, status=status.HTTP_403_FORBIDDEN)


def _bad_request(message):
    return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def order_list(request):
    """Filter opsional:
    ?buyer=true|false (default true: sebagai 'pembeli' sewa; false: sebagai pemilik),
    ?status=all|rented|requested|accepted|paid|picked-up|finished,
    ?item_id=<item_id>.
    """
    is_buyer = request.query_params.get("buyer", "true").strip().lower() == "true"
    status_filter = request.query_params.get("status", "all").strip()
    item_id = request.query_params.get("item_id", "").strip()

    queryset = Order.objects.select_related("item__owner", "buyer")

    if item_id and item_id != "-1":
        if not item_id.isdigit():
            return _bad_request("item_id harus berupa angka.")
        queryset = queryset.filter(item_id=int(item_id))

    if is_buyer:
        queryset = queryset.filter(buyer=request.user)
    else:
        queryset = queryset.filter(item__owner=request.user)

    if status_filter == "rented":
        queryset = queryset.filter(status__in=["accepted", "paid", "picked-up"])
    elif status_filter != "all":
        queryset = queryset.filter(status=status_filter)

    return Response(OrderSerializer(queryset, many=True, context={"request": request}).data)


@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def decline_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id)

    if request.user != order.item.owner:
        return _forbidden("Hanya pemilik barang yang dapat menolak pengajuan.")
    if order.status != "requested":
        return _bad_request("Order tidak dalam status pengajuan.")

    declined_id = order.id
    order.delete()
    return Response({"id": declined_id}, status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def accept_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id)

    if request.user != order.item.owner:
        return _forbidden("Hanya pemilik barang yang dapat menyetujui pengajuan.")
    if order.status != "requested":
        return _bad_request("Order tidak dalam status pengajuan.")

    with transaction.atomic():
        order.status = "accepted"
        order.save()

        item = order.item
        item.is_available = False
        item.save()

        # Semua permintaan order lain untuk barang ini otomatis ditolak
        item.orders.filter(status="requested").exclude(id=order.id).delete()

    return Response(_serialize(order, request), status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def pay_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id)

    if request.user != order.buyer:
        return _forbidden("Hanya penyewa yang dapat membayar order ini.")
    if order.status != "accepted":
        return _bad_request("Order tidak dalam status menunggu pembayaran.")

    order.status = "paid"
    order.save()
    return Response(_serialize(order, request), status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def pick_up_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id)

    if request.user != order.buyer:
        return _forbidden("Hanya penyewa yang dapat mengambil barang ini.")
    if order.status != "paid":
        return _bad_request("Order tidak dalam status menunggu pengambilan barang.")

    order.status = "picked-up"
    order.save()
    return Response(_serialize(order, request), status=status.HTTP_200_OK)


@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def finish_order(request, order_id):
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id)

    if request.user != order.item.owner:
        return _forbidden("Hanya pemilik barang yang dapat menyelesaikan sewa.")
    if order.status != "picked-up":
        return _bad_request("Order tidak sedang dipakai.")

    with transaction.atomic():
        order.status = "finished"
        order.save()

        item = order.item
        item.is_available = True
        item.save()

    return Response(_serialize(order, request), status=status.HTTP_200_OK)
