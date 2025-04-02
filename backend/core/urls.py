"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.views import APIView
from rest_framework.response import Response

class APIRootView(APIView):
    """
    API kök görünümü - İstenen yapıda endpointleri listelemek için özelleştirilmiştir
    """
    def get(self, request, format=None):
        data = {
            'profil': request.build_absolute_uri('/api/profil/'),
            'hesap': request.build_absolute_uri('/api/hesap/'),
        }
        return Response(data)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # Browsable API için
    path('api/rest-auth/', include('dj_rest_auth.urls')),  # Güncellenmiş paket kullanımı
    path('api/rest-auth/registration/', include('dj_rest_auth.registration.urls')),  # Bu satır düzeltildi
    
    # Özel API kök görünümü
    path('api/', APIRootView.as_view(), name='api-root'),
    
    # Profiller uygulaması
    path('api/profil/', include('profiller.api.urls')),
    
    # Hesaplama uygulaması
    path('api/hesap/', include('hesaplama.api.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
