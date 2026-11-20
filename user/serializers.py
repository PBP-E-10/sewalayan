from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.html import strip_tags
from rest_framework import serializers

from .models import Profile


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, value):
        value = value.strip()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username sudah dipakai.")
        return value

    def validate(self, attrs):
        if attrs["password1"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": ["Konfirmasi password tidak sama."]}
            )
        try:
            validate_password(attrs["password1"], user=User(username=attrs["username"]))
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password1": list(exc.messages)})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password1"],
        )
        Profile.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id", "username", "bio", "phone_number",
            "profile_picture", "location", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_bio(self, value):
        return strip_tags(value)

    def validate_location(self, value):
        return strip_tags(value)

    def get_profile_picture(self, obj):
        if not obj.profile_picture:
            return None
        request = self.context.get("request")
        url = obj.profile_picture.url
        return request.build_absolute_uri(url) if request else url

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        is_owner = (
            request is not None
            and request.user.is_authenticated
            and instance.user_id == request.user.id
        )
        if not is_owner:
            data.pop("phone_number", None)
        return data