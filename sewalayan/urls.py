"""
URL configuration for sewalayan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

from sewalayan.views import design_page, landing_page

urlpatterns = [
    path('', landing_page, name='landing'),
    path('design', design_page),
    path('admin/', admin.site.urls),
    path('item/', include('item.urls')),
    path('order/', include('order.urls')),
    path('review/api/', include('review.api_urls')),
    path('review/', include('review.urls')),
    path('user/', include('user.urls')),
    path('user/api/', include('user.api_urls')),
    path('user/', include('user.urls')),
]

urlpatterns += [
    path('api/v1/', include('item.api_urls')),
    path('api/v1/auth/token/', obtain_auth_token, name='api_token_auth'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
