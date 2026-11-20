from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from order.models import Order

from .models import Report, Review
from .serializers import ReportSerializer, ReviewSerializer

# Sama dengan user/api_views.py: Flutter kirim "Authorization: Token <key>",
# situs web tetap bisa pakai session.
AUTH = [TokenAuthentication, SessionAuthentication]


# ---------- Review ----------

@api_view(["GET"])
@authentication_classes(AUTH)
@permission_classes([AllowAny])
def review_list(request):
    """Daftar ulasan. Filter opsional: ?item=<item_id>, ?mine=1."""
    queryset = Review.objects.select_related("reviewer", "order__item")

    item_id = request.query_params.get("item", "").strip()
    if item_id.isdigit():
        queryset = queryset.filter(order__item_id=int(item_id))

    if request.query_params.get("mine") == "1":
        if not request.user.is_authenticated:
            return Response({"detail": "Kamu harus login dulu."}, status=status.HTTP_403_FORBIDDEN)
        queryset = queryset.filter(reviewer=request.user)

    serializer = ReviewSerializer(queryset, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET", "DELETE"])
@authentication_classes(AUTH)
@permission_classes([AllowAny])
def review_detail(request, review_id):
    review = get_object_or_404(Review.objects.select_related("reviewer", "order__item"), pk=review_id)

    if request.method == "GET":
        return Response(ReviewSerializer(review, context={"request": request}).data)

    # DELETE
    if not request.user.is_authenticated:
        return Response({"detail": "Kamu harus login dulu."}, status=status.HTTP_403_FORBIDDEN)
    if review.reviewer_id != request.user.id:
        return Response({"detail": "Hanya penulis ulasan yang dapat menghapus ulasan ini."},
                        status=status.HTTP_403_FORBIDDEN)
    review.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST", "PATCH"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def order_review(request, order_id):
    """GET lihat ulasan, POST tulis baru (order harus finished), PATCH edit."""
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id, buyer=request.user)
    review = Review.objects.filter(order=order).first()

    if request.method == "GET":
        if review is None:
            return Response({"detail": "Order ini belum diulas."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ReviewSerializer(review, context={"request": request}).data)

    if request.method == "POST":
        if review is not None:
            return Response({"detail": "Order ini sudah diulas. Gunakan PATCH untuk mengubah."},
                            status=status.HTTP_400_BAD_REQUEST)
        if order.status != "finished":
            return Response({"detail": "Ulasan hanya bisa ditulis setelah sewa selesai."},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = ReviewSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save(reviewer=request.user, order=order)
        return Response(ReviewSerializer(review, context={"request": request}).data,
                        status=status.HTTP_201_CREATED)

    # PATCH
    if review is None:
        return Response({"detail": "Order ini belum diulas."}, status=status.HTTP_404_NOT_FOUND)
    serializer = ReviewSerializer(review, data=request.data, partial=True, context={"request": request})
    serializer.is_valid(raise_exception=True)
    review = serializer.save()
    return Response(ReviewSerializer(review, context={"request": request}).data)


# ---------- Report ----------

@api_view(["GET"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def report_list(request):
    """Laporan yang dibuat user yang sedang login (Laporan Saya)."""
    queryset = Report.objects.filter(reporter=request.user).select_related("order__item", "order__buyer")
    return Response(ReportSerializer(queryset, many=True, context={"request": request}).data)


@api_view(["GET"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def report_detail(request, report_id):
    report = get_object_or_404(Report, pk=report_id, reporter=request.user)
    return Response(ReportSerializer(report, context={"request": request}).data)


@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def order_report_create(request, order_id):
    """Buat laporan untuk satu order (padanan create_report_ajax)."""
    order = get_object_or_404(Order.objects.select_related("item"), id=order_id)

    if request.user not in (order.buyer, order.item.owner):
        return Response({"detail": "Hanya penyewa atau pemilik barang yang bisa melapor."},
                        status=status.HTTP_403_FORBIDDEN)
    if Report.objects.filter(order=order, reporter=request.user, status__in=["open", "in_review"]).exists():
        return Response({"detail": "Kamu sudah punya laporan aktif untuk order ini."},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = ReportSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    report = serializer.save(reporter=request.user, order=order)

    order.item.is_available = False
    order.item.save()

    return Response(ReportSerializer(report, context={"request": request}).data,
                    status=status.HTTP_201_CREATED)