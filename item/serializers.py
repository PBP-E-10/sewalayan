from decimal import Decimal
from django.utils.html import strip_tags
from rest_framework import serializers

from .grading import calculate_condition_grade, is_eligible
from .models import Category, Item


class ItemSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True, default="")
    image_url = serializers.SerializerMethodField()
    is_rented = serializers.BooleanField(read_only=True)

    class Meta:
        model = Item
        fields = [
            "id",
            "owner",
            "owner_username",
            "category",
            "category_name",
            "name",
            "description",
            "price_per_day",
            "functional_score",
            "physical_score",
            "safety_score",
            "completeness_score",
            "hygiene_score",
            "condition_grade",
            "is_available",
            "is_rented",
            "location",
            "latitude",
            "longitude",
            "image",
            "image_url",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_username",
            "category_name",
            "condition_grade",
            "is_rented",
            "latitude",
            "longitude",
            "image_url",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image and hasattr(obj.image, "url"):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return ""

    def validate_name(self, value):
        cleaned = strip_tags(value).strip()
        if not cleaned:
            raise serializers.ValidationError("Nama barang tidak boleh kosong.")
        return cleaned

    def validate_description(self, value):
        cleaned = strip_tags(value).strip()
        if not cleaned:
            raise serializers.ValidationError("Deskripsi tidak boleh kosong.")
        return cleaned

    def validate_location(self, value):
        cleaned = strip_tags(value).strip()
        if not cleaned:
            raise serializers.ValidationError("Lokasi tidak boleh kosong.")
        return cleaned

    def validate_price_per_day(self, value):
        if value <= Decimal("0"):
            raise serializers.ValidationError("Harga sewa harus lebih dari 0.")
        return value

    def validate(self, attrs):
        instance = self.instance or Item()
        for attr, val in attrs.items():
            setattr(instance, attr, val)
        if not is_eligible(instance):
            raise serializers.ValidationError(
                "Barang dengan kondisi ini tidak layak disewakan. "
                "Periksa kembali skor Keamanan, Fungsi, dan Kebersihan."
            )
        return attrs

    def create(self, validated_data):
        item = Item(**validated_data)
        item.condition_grade = calculate_condition_grade(item)
        item.save()
        return item

    def update(self, instance, validated_data):
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.condition_grade = calculate_condition_grade(instance)
        instance.save()
        return instance