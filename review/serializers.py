from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Report, Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(source="order.id", read_only=True, default=None)
    item_id = serializers.IntegerField(source="order.item_id", read_only=True, default=None)
    item_name = serializers.CharField(source="order.item.name", read_only=True, default="-")
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ["id", "reviewer", "reviewer_username", "order_id", "item_id",
                  "item_name", "rating", "comment", "created_at", "is_owner"]
        read_only_fields = ["id", "reviewer", "created_at"]

    def get_reviewer_username(self, obj):
        return obj.reviewer.username if obj.reviewer else "Anonim"

    def get_is_owner(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.reviewer_id == request.user.id

    def validate_comment(self, value):
        return strip_tags(value).strip()


class ReportSerializer(serializers.ModelSerializer):
    reporter_username = serializers.CharField(source="reporter.username", read_only=True)
    reported_username = serializers.SerializerMethodField()
    order_id = serializers.UUIDField(source="order.id", read_only=True)
    item_name = serializers.CharField(source="order.item.name", read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Report
        fields = ["id", "reporter", "reporter_username", "reported_username",
                  "order_id", "item_name", "reason", "reason_display",
                  "description", "status", "status_display", "admin_note", "created_at"]
        read_only_fields = ["id", "reporter", "status", "admin_note", "created_at"]

    def get_reported_username(self, obj):
        return obj.reported_user.username

    def validate_description(self, value):
        cleaned = strip_tags(value).strip()
        if not cleaned:
            raise serializers.ValidationError("Keterangan laporan tidak boleh kosong.")
        return cleaned