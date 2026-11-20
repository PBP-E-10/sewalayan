from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    item_id = serializers.IntegerField(source="item.id", read_only=True)
    item_name = serializers.CharField(source="item.name", read_only=True)
    owner = serializers.CharField(source="item.owner.username", read_only=True)
    buyer = serializers.CharField(source="buyer.username", read_only=True)
    status_display = serializers.CharField(source="status_id", read_only=True)
    status_details = serializers.CharField(read_only=True)
    is_buyer = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "item_id", "item_name", "owner", "buyer",
                  "status", "status_display", "status_details",
                  "purchase_price", "created_at", "taken_at", "returned_at",
                  "is_buyer", "is_owner"]
        read_only_fields = fields

    def get_is_buyer(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated
                    and obj.buyer_id == request.user.id)

    def get_is_owner(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated
                    and obj.item.owner_id == request.user.id)
