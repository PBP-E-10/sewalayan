from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from .grading import NOT_ELIGIBLE_GRADE
from .models import Item
from .permissions import IsOwnerOrReadOnly
from .serializers import ItemSerializer
from .views import _has_unfinished_orders, _parse_decimal, geocode_address


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsOwnerOrReadOnly])
def item_list(request):
    if request.method in ("GET", "HEAD"):
        queryset = (
            Item.objects.select_related("owner", "category")
            .exclude(condition_grade=NOT_ELIGIBLE_GRADE)
            .order_by("-created_at", "-id")
        )
        q = request.query_params.get("q", "").strip()[:100]
        category = request.query_params.get("category", "").strip()
        grade = request.query_params.get("grade", "").strip()[:100]
        location = request.query_params.get("location", "").strip()[:100]
        min_price = _parse_decimal(request.query_params.get("min_price", "").strip())
        max_price = _parse_decimal(request.query_params.get("max_price", "").strip())

        if q:
            queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category.isascii() and category.isdigit():
            queryset = queryset.filter(category_id=int(category))
        if min_price is not None:
            queryset = queryset.filter(price_per_day__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price_per_day__lte=max_price)
        if grade:
            queryset = queryset.filter(condition_grade__startswith=grade)
        if location:
            queryset = queryset.filter(location__icontains=location)

        serializer = ItemSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = ItemSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    item = serializer.save(owner=request.user)
    if item.location:
        lat, lon = geocode_address(item.location)
        if lat is not None and lon is not None:
            item.latitude = lat
            item.longitude = lon
            item.save(update_fields=["latitude", "longitude"])
    output = ItemSerializer(item, context={"request": request})
    return Response(output.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsOwnerOrReadOnly])
def item_detail(request, item_id):
    item = get_object_or_404(Item.objects.select_related("owner", "category"), pk=item_id)

    if request.method in ("GET", "HEAD"):
        serializer = ItemSerializer(item, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        if not (item.owner == request.user or request.user.is_superuser):
            return Response(
                {"detail": IsOwnerOrReadOnly.message},
                status=status.HTTP_403_FORBIDDEN,
            )
        if _has_unfinished_orders(item):
            return Response(
                {"detail": "Barang tidak bisa dihapus karena masih ada penyewaan yang belum selesai."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if not (item.owner == request.user or request.user.is_superuser):
        return Response(
            {"detail": IsOwnerOrReadOnly.message},
            status=status.HTTP_403_FORBIDDEN,
        )

    old_location = item.location
    serializer = ItemSerializer(
        item,
        data=request.data,
        partial=(request.method == "PATCH"),
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    updated_item = serializer.save()
    if updated_item.location != old_location:
        lat, lon = geocode_address(updated_item.location)
        updated_item.latitude = lat
        updated_item.longitude = lon
        updated_item.save(update_fields=["latitude", "longitude"])

    output = ItemSerializer(updated_item, context={"request": request})
    return Response(output.data, status=status.HTTP_200_OK)