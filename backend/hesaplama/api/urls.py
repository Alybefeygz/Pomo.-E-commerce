from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    KargoFirmaViewSet, DesiKgDegerViewSet, DesiKgKargoUcretViewSet, KargoUcretHesaplamaView,
    KategoriViewSet, AltKategoriViewSet, UrunGrubuViewSet, KomisyonOraniViewSet,
    KategoriKomisyonBulmaView, SatisFiyatBelirlemeView, KullaniciHesaplamalariViewSet,
    AltKategoriListView, UrunGrubuListView, EksikHesaplamaView
)

# Admin router for admin endpoints
admin_router = DefaultRouter()
admin_router.register('kargo-firma', KargoFirmaViewSet, basename='admin-kargo-firma')
admin_router.register('desi-kg-deger', DesiKgDegerViewSet, basename='admin-desi-kg-deger')
admin_router.register('kargo-ucret', DesiKgKargoUcretViewSet, basename='admin-kargo-ucret')
admin_router.register('kategoriler', KategoriViewSet, basename='admin-kategori')
admin_router.register('alt-kategoriler', AltKategoriViewSet, basename='admin-alt-kategori')
admin_router.register('urun-gruplari', UrunGrubuViewSet, basename='admin-urun-grubu')
admin_router.register('komisyon-oranlari', KomisyonOraniViewSet, basename='admin-komisyon-orani')
admin_router.register('kullanici-islemleri', KullaniciHesaplamalariViewSet, basename='admin-kullanici-islemleri')

@api_view(['GET'])
def api_root(request, format=None):
    """
    API root that shows admin and user-specific endpoints
    """
    # Kullanıcı giriş yapmışsa kendi username'ini, yapmamışsa 'username-guest' kullan
    username = f'username-{request.user.username}' if request.user.is_authenticated else 'username-guest'
    
    return Response({
        'admin': reverse('admin-root', request=request, format=format),
        'kullanıcı': reverse('user-root', request=request, kwargs={'username': username}, format=format),
    })

@api_view(['GET'])
def admin_root(request, format=None):
    """
    Admin root that shows all admin endpoints
    """
    return Response({
        'kargo-firma': reverse('admin-kargo-firma-list', request=request, format=format),
        'desi-kg-deger': reverse('admin-desi-kg-deger-list', request=request, format=format),
        'kargo-ucret': reverse('admin-kargo-ucret-list', request=request, format=format),
        'kategoriler': reverse('admin-kategori-list', request=request, format=format),
        'alt-kategoriler': reverse('admin-alt-kategori-list', request=request, format=format),
        'urun-gruplari': reverse('admin-urun-grubu-list', request=request, format=format),
        'komisyon-oranlari': reverse('admin-komisyon-orani-list', request=request, format=format),
        'kullanici-islemleri': reverse('admin-kullanici-islemleri-list', request=request, format=format),
        'eksik-hesaplama': reverse('admin-eksik-hesaplama', request=request, format=format),
    })

@api_view(['GET'])
def user_root(request, username, format=None):
    """
    User root that shows user-specific endpoints
    """
    # Remove 'username-' prefix for generating URLs
    actual_username = username.replace('username-', '', 1)
    return Response({
        'kargo-ucret-hesap': reverse('user-kargo-ucret-hesap', request=request, kwargs={'username': username}, format=format),
        'kategori-komisyon-orani-bulma': reverse('user-kategori-komisyon-orani-bulma', request=request, kwargs={'username': username}, format=format),
        'satis-fiyat-belirleme': reverse('user-satis-fiyat-belirleme', request=request, kwargs={'username': username}, format=format),
    })

urlpatterns = [
    # API root viewset
    path('', api_root, name='hesap-api-root'),
    
    # Admin endpoints
    path('admin/', admin_root, name='admin-root'),
    path('admin/', include(admin_router.urls)),
    path('admin/eksik-hesaplama/', EksikHesaplamaView.as_view(), name='admin-eksik-hesaplama'),
    
    # User-specific endpoints
    path('<str:username>/', user_root, name='user-root'),
    path('<str:username>/kargo-ucret-hesap/', KargoUcretHesaplamaView.as_view(), name='user-kargo-ucret-hesap'),
    path('<str:username>/kategori-komisyon-orani-bulma/', KategoriKomisyonBulmaView.as_view(), name='user-kategori-komisyon-orani-bulma'),
    path('<str:username>/satis-fiyat-belirleme/', SatisFiyatBelirlemeView.as_view(), name='user-satis-fiyat-belirleme'),
    
    # Dynamic dropdown endpoints
    path('kategoriler/<int:kategori_id>/alt-kategoriler/', AltKategoriListView.as_view(), name='alt-kategori-list'),
    path('alt-kategoriler/<int:alt_kategori_id>/urun-gruplari/', UrunGrubuListView.as_view(), name='urun-grubu-list'),
] 