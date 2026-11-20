from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Profile
from .serializers import LoginSerializer, ProfileSerializer, RegisterSerializer

AUTH = [TokenAuthentication, SessionAuthentication]


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {"id": user.id, "username": user.username},
        status=status.HTTP_201_CREATED,
    )

@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def login_api(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(
        request,
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"],
    )
    if user is None:
        return Response(
            {"detail": "Username atau password salah."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if not user.is_active:
        return Response(
            {"detail": "Akun ini dinonaktifkan."},
            status=status.HTTP_403_FORBIDDEN,
        )
    login(request, user)
    token, _ = Token.objects.get_or_create(user=user)
    profile, _ = Profile.objects.get_or_create(user=user)
    return Response({
        "token": token.key,
        "user": {"id": user.id, "username": user.username},
        "profile_id": str(profile.id),
    })

@api_view(["POST"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def logout_api(request):
    Token.objects.filter(user=request.user).delete()
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "HEAD", "PATCH"])
@authentication_classes(AUTH)
@permission_classes([IsAuthenticated])
def me_api(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == "PATCH":
        serializer = ProfileSerializer(
            profile, data=request.data, partial=True, context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    return Response(ProfileSerializer(profile, context={"request": request}).data)

@api_view(["GET", "HEAD"])
@authentication_classes(AUTH)
@permission_classes([AllowAny])
def profile_detail_api(request, profile_id):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=profile_id)
    return Response(ProfileSerializer(profile, context={"request": request}).data)

