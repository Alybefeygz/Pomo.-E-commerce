from rest_framework import viewsets, status, filters, permissions
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Q
from hesaplama.models import KargoFirma, DesiKgDeger, DesiKgKargoUcret, Kategori, AltKategori, UrunGrubu, KomisyonOrani, Hesaplamalar, Pazaryeri, PazaryeriKargofirma, KargoHesaplamaGecmisi
from .serializers import (
    PazaryeriSerializer, KargoFirmaSerializer, DesiKgDegerSerializer,
    DesiKgKargoUcretSerializer, PazaryeriKargofirmaSerializer,
    KargoUcretHesaplamaSerializer, KategoriSerializer, AltKategoriSerializer,
    UrunGrubuSerializer, KomisyonOraniSerializer,
    KategoriKomisyonBulmaSerializer, UserHesaplamalarSerializer, EksikHesaplamaSerializer, KargoUcretEklemeSerializer, KomisyonEklemeSerializer,
    KomisyonOraniBulmaSerializer, FiyatHesaplamaSerializer, DesiKgHesaplamaSerializer, MarketplacePriceCalculationSerializer
)
from .permissions import IsSuperUserOrReadOnly
import math
from decimal import Decimal
from rest_framework import serializers
import logging
from rest_framework import renderers
import pandas as pd
from django.utils import timezone
from hesaplama.models import HesaplamaKategoriSeviyeleri, HesaplamaKategoriler, HesaplamaKomisyonOranlari
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime, timedelta
from hesaplama.utils import check_and_link_calculations

# Mixin to validate username in URL
class UsernameMixin:
    def validate_username(self, username):
        # Remove 'username-' prefix to get actual username
        actual_username = username.replace('username-', '', 1)
        
        # Eğer guest kullanıcısı ise doğrulama yapmadan geç
        if actual_username == 'guest':
            return None
            
        # Giriş yapmış kullanıcılar için kontrol
        if self.request.user.is_authenticated:
            # Get user from URL
            User = get_user_model()
            get_object_or_404(User, username=actual_username)
            return None
        else:
            # Giriş yapmamış kullanıcılar için herhangi bir kısıtlama yok
            return None

class PazaryeriViewSet(viewsets.ModelViewSet):
    """
    Pazar yerlerini listeler, oluşturur, günceller ve siler.
    """
    queryset = Pazaryeri.objects.all().order_by('pazar_ismi')
    serializer_class = PazaryeriSerializer
    permission_classes = [IsAdminUser]

class KargoFirmaViewSet(viewsets.ModelViewSet):
    """
    Kargo firmalarını listeler, oluşturur, günceller ve siler.
    """
    queryset = KargoFirma.objects.all().order_by('firma_ismi')
    serializer_class = KargoFirmaSerializer
    permission_classes = [IsAdminUser]

class DesiKgDegerViewSet(viewsets.ModelViewSet):
    """
    Desi-Kg değerlerini listeler, oluşturur, günceller ve siler.
    """
    queryset = DesiKgDeger.objects.all().order_by('pazar_yeri', 'desi_degeri')
    serializer_class = DesiKgDegerSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """
        Opsiyonel filtreleme sağlar:
        - pazar_yeri parametresi ile pazar yeri ID'sine göre
        """
        queryset = DesiKgDeger.objects.all()
        pazar_yeri_id = self.request.query_params.get('pazar_yeri')
        
        if pazar_yeri_id:
            queryset = queryset.filter(pazar_yeri_id=pazar_yeri_id)
            
        return queryset

class DesiKgKargoUcretViewSet(viewsets.ModelViewSet):
    """
    Desi-Kg ve kargo ücretlerini listeler, oluşturur, günceller ve siler.
    """
    queryset = DesiKgKargoUcret.objects.all()
    serializer_class = DesiKgKargoUcretSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """
        Opsiyonel filtreleme sağlar:
        - pazar_yeri parametresi ile pazar yeri ID'sine göre
        - kargo_firma parametresi ile kargo firma ID'sine göre
        - desi_kg_deger parametresi ile desi/kg değerine göre
        """
        queryset = DesiKgKargoUcret.objects.all()
        
        pazar_yeri_id = self.request.query_params.get('pazar_yeri')
        kargo_firma_id = self.request.query_params.get('kargo_firma')
        desi_kg_deger_id = self.request.query_params.get('desi_kg_deger')
        
        if pazar_yeri_id:
            queryset = queryset.filter(pazar_yeri_id=pazar_yeri_id)
            
        if kargo_firma_id:
            queryset = queryset.filter(kargo_firma_id=kargo_firma_id)
            
        if desi_kg_deger_id:
            queryset = queryset.filter(desi_kg_deger_id=desi_kg_deger_id)
            
        return queryset

class PazaryeriKargofirmaViewSet(viewsets.ModelViewSet):
    """
    Pazar yeri ve kargo firma ilişkilerini listeler, oluşturur, günceller ve siler.
    """
    queryset = PazaryeriKargofirma.objects.all()
    serializer_class = PazaryeriKargofirmaSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """
        Opsiyonel filtreleme sağlar:
        - pazar_yeri parametresi ile pazar yeri ID'sine göre
        - kargo_firma parametresi ile kargo firma ID'sine göre
        """
        queryset = PazaryeriKargofirma.objects.all()
        
        pazar_yeri_id = self.request.query_params.get('pazar_yeri')
        kargo_firma_id = self.request.query_params.get('kargo_firma')
        
        if pazar_yeri_id:
            queryset = queryset.filter(pazar_yeri_id=pazar_yeri_id)
            
        if kargo_firma_id:
            queryset = queryset.filter(kargo_firma_id=kargo_firma_id)
            
        return queryset

class KargoUcretHesaplamaView(UsernameMixin, APIView):
    """
    Kargo ücreti hesaplama endpoint'i için view
    """
    permission_classes = [AllowAny]
    serializer_class = KargoUcretHesaplamaSerializer
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def validate_email(self, email):
        """
        Email adresinin sistemde kayıtlı olup olmadığını kontrol eder
        """
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            return True, None  # Email kayıtlı ise hesaplama yapılabilir
        return True, None  # Email kayıtlı değilse de hesaplama yapılabilir

    def get(self, request, username=None, format=None):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        serializer = self.serializer_class()
        return Response(serializer.to_representation(None))

    def post(self, request, username=None, format=None):
        """
        POST isteği için hesaplama yapar ve sonuçları döndürür
        """
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Email kontrolü
                email = serializer.validated_data.get('email', '').strip().lower()
                
                # Hesaplama geçmişi kontrolü ve bağlama
                if not check_and_link_calculations(request.user, email):
                    return Response(
                        {'error': 'Girdiğiniz email adresi ile giriş yaptığınız email adresi eşleşmiyor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Form verilerini al
                desi_kg_degeri = serializer.validated_data['desi_kg_degeri']
                pazar_yeri = serializer.validated_data['pazar_yeri']
                kargo_firma = serializer.validated_data['kargo_firma']
                
                # Desi/Kg değerini tam sayıya yuvarla
                desi_kg_yuvarlama = math.ceil(desi_kg_degeri)
                
                # Pazar yeri ve kargo firma ilişkisini kontrol et
                if not PazaryeriKargofirma.objects.filter(pazar_yeri=pazar_yeri, kargo_firma=kargo_firma).exists():
                    return Response(
                        {'error': f'{kargo_firma.firma_ismi} {pazar_yeri.pazar_ismi} için hizmet vermemektedir.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Desi/Kg değerini bul
                desi_kg_deger = DesiKgDeger.objects.filter(
                    pazar_yeri=pazar_yeri,
                    desi_degeri=desi_kg_yuvarlama
                ).first()
                
                if not desi_kg_deger:
                    return Response(
                        {'error': f'{pazar_yeri.pazar_ismi} için {desi_kg_yuvarlama} desi/kg değerinde tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Kargo ücretini bul
                kargo_ucret = DesiKgKargoUcret.objects.filter(
                    pazar_yeri=pazar_yeri,
                    kargo_firma=kargo_firma,
                    desi_kg_deger=desi_kg_deger
                ).first()
                
                if not kargo_ucret:
                    return Response(
                        {'error': f'{pazar_yeri.pazar_ismi} - {kargo_firma.firma_ismi} için {desi_kg_yuvarlama} desi/kg değerinde tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Hesaplama geçmişini kaydet
                from hesaplama.models import KargoUcretGecmis
                KargoUcretGecmis.objects.create(
                    kullanici=request.user if request.user.is_authenticated else None,
                    email=email,
                    urun_ismi=serializer.validated_data.get('urun_ismi', 'Ürün'),
                    desi_kg_degeri=desi_kg_degeri,
                    yuvarlanmis_desi_kg=desi_kg_yuvarlama,
                    pazar_yeri=pazar_yeri,
                    kargo_firma=kargo_firma,
                    kargo_ucreti=kargo_ucret.ucret
                )
                
                # Sonuçları döndür
                result = {
                    'email': email,
                    'urun_ismi': serializer.validated_data.get('urun_ismi', 'Ürün'),
                    'desi_kg_degeri': desi_kg_degeri,
                    'yuvarlanmis_desi_kg': desi_kg_yuvarlama,
                    'pazar_yeri': pazar_yeri.pazar_ismi,
                    'kargo_firma': kargo_firma.firma_ismi,
                    'kargo_ucreti': kargo_ucret.ucret
                }
                
                return Response(result)
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Trendyol Kategori Komisyon Oranları için ViewSet'ler
class KategoriViewSet(viewsets.ModelViewSet):
    """
    Trendyol kategorilerini listeler, oluşturur, günceller ve siler.
    """
    queryset = Kategori.objects.all().order_by('kategori_adi')
    serializer_class = KategoriSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, methods=['get'])
    def alt_kategoriler(self, request, pk=None):
        """
        Belirli bir kategoriye ait alt kategorileri listeler.
        """
        kategori = self.get_object()
        alt_kategoriler = AltKategori.objects.filter(kategori=kategori)
        serializer = AltKategoriSerializer(alt_kategoriler, many=True)
        return Response(serializer.data)

class AltKategoriViewSet(viewsets.ModelViewSet):
    """
    Alt kategorileri listeler, oluşturur, günceller ve siler.
    """
    queryset = AltKategori.objects.all()
    serializer_class = AltKategoriSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """
        Opsiyonel filtreleme sağlar:
        - kategori parametresi ile kategori ID'sine göre
        """
        queryset = AltKategori.objects.all()
        
        # URL parametrelerini al
        kategori_id = self.request.query_params.get('kategori')
        
        # Kategori ID'sine göre filtrele
        if kategori_id:
            queryset = queryset.filter(kategori_id=kategori_id)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def urun_gruplari(self, request, pk=None):
        """
        Belirli bir alt kategoriye ait ürün gruplarını listeler.
        """
        alt_kategori = self.get_object()
        urun_gruplari = UrunGrubu.objects.filter(alt_kategori=alt_kategori)
        serializer = UrunGrubuSerializer(urun_gruplari, many=True)
        return Response(serializer.data)

class UrunGrubuViewSet(viewsets.ModelViewSet):
    """
    Ürün gruplarını listeler, oluşturur, günceller ve siler.
    """
    queryset = UrunGrubu.objects.all()
    serializer_class = UrunGrubuSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """
        Opsiyonel filtreleme sağlar:
        - alt_kategori parametresi ile alt kategori ID'sine göre
        """
        queryset = UrunGrubu.objects.all()
        
        # URL parametrelerini al
        alt_kategori_id = self.request.query_params.get('alt_kategori')
        
        # Alt kategori ID'sine göre filtrele
        if alt_kategori_id:
            queryset = queryset.filter(alt_kategori_id=alt_kategori_id)
            
        return queryset
    
    @action(detail=True, methods=['get'])
    def komisyon_oranlari(self, request, pk=None):
        """
        Belirli bir ürün grubuna ait komisyon oranlarını listeler.
        """
        urun_grubu = self.get_object()
        komisyon_oranlari = KomisyonOrani.objects.filter(urun_grubu=urun_grubu)
        serializer = KomisyonOraniSerializer(komisyon_oranlari, many=True)
        return Response(serializer.data)

class KomisyonOraniViewSet(viewsets.ModelViewSet):
    """
    Komisyon oranlarını listeler, oluşturur, günceller ve siler.
    """
    queryset = KomisyonOrani.objects.all()
    serializer_class = KomisyonOraniSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """
        Opsiyonel filtreleme sağlar:
        - urun_grubu parametresi ile ürün grubu ID'sine göre
        """
        queryset = KomisyonOrani.objects.all()
        
        # URL parametrelerini al
        urun_grubu_id = self.request.query_params.get('urun_grubu')
        
        # Ürün grubu ID'sine göre filtrele
        if urun_grubu_id:
            queryset = queryset.filter(urun_grubu_id=urun_grubu_id)
            
        return queryset

class KullaniciHesaplamalariViewSet(viewsets.GenericViewSet):
    """
    Kullanıcıların hesaplamalarını listeleyen ve filtreleme yapan ViewSet.
    Kullanıcı seçerek belirli bir kullanıcının hesaplamalarını görebilirsiniz.
    Misafir kullanıcıların hesaplamalarını da görüntüleyebilirsiniz.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserHesaplamalarSerializer
    permission_classes = [IsAdminUser]
    template_name = 'rest_framework/api.html'

    def list(self, request):
        # Serializer'ı oluştur
        serializer = self.get_serializer()
        
        # Seçilen kullanıcı adını ve misafir seçeneğini al
        username = request.query_params.get('username', None)
        show_guest = request.query_params.get('show_guest', 'false').lower() == 'true'
        
        # Tüm hesaplamaları al
        hesaplamalar = Hesaplamalar.objects.prefetch_related('fiyat_belirlemeler')
        
        # Filtreleme yap
        if username:
            hesaplamalar = hesaplamalar.filter(kullanici__username=username)
        elif not show_guest:
            # Eğer username seçilmemişse ve misafir hesaplamalar istenmemişse, sadece kayıtlı kullanıcıların hesaplamalarını göster
            hesaplamalar = hesaplamalar.filter(kullanici__isnull=False)
        
        # Hesaplamaları formatla
        results = []
        
        # Kayıtlı kullanıcıların hesaplamaları
        users = self.get_queryset()
        if username:
            users = users.filter(username=username)
            
        for user in users:
            user_calculations = []
            for hesaplama in hesaplamalar.filter(kullanici=user):
                fiyat_belirlemeler_data = []
                for fiyat_belirleme in hesaplama.fiyat_belirlemeler.all():
                    fiyat_belirlemeler_data.append({
                        "urun_id": fiyat_belirleme.urun_id,
                        "urun_ismi": fiyat_belirleme.urun_ismi,
                        "urun_maliyeti": float(fiyat_belirleme.urun_maliyeti),
                        "paketleme_maliyeti": float(fiyat_belirleme.paketleme_maliyeti),
                        "trendyol_hizmet_bedeli": float(fiyat_belirleme.trendyol_hizmet_bedeli),
                        "kargo_firmasi": fiyat_belirleme.kargo_firmasi,
                        "kargo_ucreti": float(fiyat_belirleme.kargo_ucreti),
                        "stopaj_degeri": float(fiyat_belirleme.stopaj_degeri),
                        "desi_kg_degeri": float(fiyat_belirleme.desi_kg_degeri),
                        "urun_kategorisi": fiyat_belirleme.urun_kategorisi,
                        "komisyon_orani": float(fiyat_belirleme.komisyon_orani),
                        "komisyon_tutari": float(fiyat_belirleme.komisyon_tutari),
                        "kdv_orani": float(fiyat_belirleme.kdv_orani),
                        "kar_orani": float(fiyat_belirleme.kar_orani),
                        "kar_tutari": float(fiyat_belirleme.kar_tutari),
                        "satis_fiyati_kdv_haric": float(fiyat_belirleme.satis_fiyati_kdv_haric),
                        "satis_fiyati_kdv_dahil": float(fiyat_belirleme.satis_fiyati_kdv_dahil)
                    })
                
                user_calculations.append({
                    "hesaplama_id": hesaplama.hesaplama_id,
                    "olusturulma_tarihi": hesaplama.olusturulma_tarihi.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "toplam_fiyat": float(hesaplama.toplam_fiyat),
                    "fiyat_belirlemeler": fiyat_belirlemeler_data
                })
            
            if user_calculations:
                results.append({
                    "kullanici_id": user.id,
                    "kullanici_name": user.username,
                    "hesaplamalar": user_calculations
                })
        
        # Misafir kullanıcıların hesaplamaları
        if show_guest and not username:
            guest_calculations = []
            for hesaplama in hesaplamalar.filter(kullanici__isnull=True):
                fiyat_belirlemeler_data = []
                for fiyat_belirleme in hesaplama.fiyat_belirlemeler.all():
                    fiyat_belirlemeler_data.append({
                        "urun_id": fiyat_belirleme.urun_id,
                        "urun_ismi": fiyat_belirleme.urun_ismi,
                        "urun_maliyeti": float(fiyat_belirleme.urun_maliyeti),
                        "paketleme_maliyeti": float(fiyat_belirleme.paketleme_maliyeti),
                        "trendyol_hizmet_bedeli": float(fiyat_belirleme.trendyol_hizmet_bedeli),
                        "kargo_firmasi": fiyat_belirleme.kargo_firmasi,
                        "kargo_ucreti": float(fiyat_belirleme.kargo_ucreti),
                        "stopaj_degeri": float(fiyat_belirleme.stopaj_degeri),
                        "desi_kg_degeri": float(fiyat_belirleme.desi_kg_degeri),
                        "urun_kategorisi": fiyat_belirleme.urun_kategorisi,
                        "komisyon_orani": float(fiyat_belirleme.komisyon_orani),
                        "komisyon_tutari": float(fiyat_belirleme.komisyon_tutari),
                        "kdv_orani": float(fiyat_belirleme.kdv_orani),
                        "kar_orani": float(fiyat_belirleme.kar_orani),
                        "kar_tutari": float(fiyat_belirleme.kar_tutari),
                        "satis_fiyati_kdv_haric": float(fiyat_belirleme.satis_fiyati_kdv_haric),
                        "satis_fiyati_kdv_dahil": float(fiyat_belirleme.satis_fiyati_kdv_dahil)
                    })
                
                guest_calculations.append({
                    "hesaplama_id": hesaplama.hesaplama_id,
                    "email": hesaplama.email,
                    "olusturulma_tarihi": hesaplama.olusturulma_tarihi.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "toplam_fiyat": float(hesaplama.toplam_fiyat),
                    "fiyat_belirlemeler": fiyat_belirlemeler_data
                })
            
            if guest_calculations:
                results.append({
                    "kullanici_name": "Misafir Kullanıcılar",
                    "hesaplamalar": guest_calculations
                })

        # Form ve sonuçları birlikte döndür
        return Response({
            'form': serializer.data,
            'results': results
        })

class AltKategoriListView(APIView):
    """
    Belirli bir kategoriye ait alt kategorileri listeleyen API view.
    """
    def get(self, request, kategori_id, format=None):
        alt_kategoriler = AltKategori.objects.filter(kategori_id=kategori_id).order_by('alt_kategori_adi')
        serializer = AltKategoriSerializer(alt_kategoriler, many=True)
        return Response(serializer.data)

class UrunGrubuListView(APIView):
    """
    Belirli bir alt kategoriye ait ürün gruplarını listeleyen API view.
    """
    def get(self, request, alt_kategori_id, format=None):
        urun_gruplari = UrunGrubu.objects.filter(alt_kategori_id=alt_kategori_id).order_by('urun_grubu_adi')
        serializer = UrunGrubuSerializer(urun_gruplari, many=True)
        return Response(serializer.data)

class EksikHesaplamaView(APIView):
    """
    Eksik hesaplama endpoint'i için view
    """
    permission_classes = [IsAdminUser]
    serializer_class = EksikHesaplamaSerializer
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def get(self, request):
        """
        GET isteği için form verilerini ve kargo firmalarını döndürür
        """
        serializer = self.serializer_class()
        return Response(serializer.data)

    def post(self, request):
        """
        POST isteği için hesaplama yapar ve sonuçları döndürür
        """
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Form verilerini al ve Decimal'e çevir
                urun_ismi = serializer.validated_data['urun_ismi']
                kdv_orani = Decimal(str(serializer.validated_data['kdv_orani']))
                urun_maliyeti = Decimal(str(serializer.validated_data['urun_maliyeti']))
                urun_paketleme_maliyeti = Decimal(str(serializer.validated_data['urun_paketleme_maliyeti']))
                desi_kg = Decimal(str(serializer.validated_data['desi_kg']))
                kargo_firma_ismi = serializer.validated_data['kargo_firma']
                istenilen_kar_orani = Decimal(str(serializer.validated_data['istenilen_kar_orani']))

                # Kargo ücretini hesapla
                desi_kg_deger = DesiKgDeger.objects.get(desi_degeri=float(desi_kg))
                kargo_firma = KargoFirma.objects.get(firma_ismi=kargo_firma_ismi)
                kargo_ucreti = DesiKgKargoUcret.objects.get(
                    desi_kg_deger=desi_kg_deger,
                    kargo_firma=kargo_firma
                ).fiyat

                # Hesaplamaları yap
                tam_kisim = (urun_maliyeti + urun_paketleme_maliyeti + Decimal(str(kargo_ucreti))) * Decimal('100')
                yuzdelik_kisim = Decimal('100') - (Decimal('1') + istenilen_kar_orani)
                satis_fiyati = tam_kisim / yuzdelik_kisim
                kdv_dahil_satis_fiyati = satis_fiyati * (Decimal('100') + kdv_orani) / Decimal('100')

                # Stopaj ve kar hesaplamaları
                stopaj = Decimal('1.0')
                stopaj_ucreti = satis_fiyati * stopaj / Decimal('100')
                kar_tutari = satis_fiyati * istenilen_kar_orani / Decimal('100')
                kdv_tutari = satis_fiyati * kdv_orani / Decimal('100')

                return Response({
                    'urun_ismi': urun_ismi,
                    'urun_maliyeti': float(urun_maliyeti),
                    'Paketleme Maliyeti': float(urun_paketleme_maliyeti),
                    'Desi/Kg Değeri': float(desi_kg),
                    'Kargo Firması': kargo_firma_ismi,
                    'Kargo Ücreti': float(kargo_ucreti),
                    'Stopaj': float(stopaj),
                    'Stopaj Ücreti': float(stopaj_ucreti),
                    'Kar Oranı': float(istenilen_kar_orani),
                    'Kar Tutarı': float(kar_tutari),
                    'Belirlenen KDV Tutarı': float(kdv_orani),
                    'KDV fiyatı': float(kdv_tutari),
                    'Satış Fiyatı(KDV Dahil değil)': float(satis_fiyati),
                    'Satış Fiyatı(KDV Dahil)': float(kdv_dahil_satis_fiyati)
                })

            except (ValueError, DesiKgDeger.DoesNotExist, KargoFirma.DoesNotExist, DesiKgKargoUcret.DoesNotExist) as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KargoUcretEklemeView(APIView):
    """
    Kargo ücreti ekleme endpoint'i için view
    """
    permission_classes = [IsAdminUser]
    serializer_class = KargoUcretEklemeSerializer
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def get(self, request):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        serializer = self.serializer_class()
        response_data = serializer.data
        response_data['uyari_mesaji'] = (
            "Yüklenecek excelde kargo firma isimleri aşağıdaki kargo firmalarını içeriyorsa "
            "kargo firma isimleri bu şekilde yazılmalıdır:\n"
            "Aras\n"
            "Kolay Gelsin\n"
            "MNG\n"
            "PTT\n"
            "Sürat\n"
            "TEX\n"
            "Yurtiçi\n"
            "Borusan\n"
            "CEVA\n"
            "Horoz\n"
            "hepsiJET\n"
            "hepsiJET XL"
        )
        return Response(response_data)

    def find_matching_kargo_firma(self, kargo_firma_adi):
        """
        Verilen kargo firma adına en uygun eşleşmeyi bulur.
        """
        # Kargo firma adını normalize et (küçük harfe çevir)
        normalized_input = kargo_firma_adi.lower().strip()
        
        # Veritabanındaki tüm kargo firmalarını al
        all_kargo_firmalari = KargoFirma.objects.all()
        
        # HepsiJET ve HepsiJET XL için özel kontrol
        if 'hepsijet' in normalized_input:
            if 'xl' in normalized_input:
                return KargoFirma.objects.filter(firma_ismi='HepsiJET XL').first()
            else:
                return KargoFirma.objects.filter(firma_ismi='HepsiJET').first()
        
        # Diğer firmalar için içinde geçme kontrolü
        for firma in all_kargo_firmalari:
            # Mevcut firma adını normalize et
            normalized_firma = firma.firma_ismi.lower().strip()
            
            # Tam eşleşme kontrolü
            if normalized_input == normalized_firma:
                return firma
            
            # İçinde geçme kontrolü (HepsiJET ve HepsiJET XL hariç)
            if firma.firma_ismi not in ['HepsiJET', 'HepsiJET XL']:
                if normalized_firma in normalized_input or normalized_input in normalized_firma:
                    return firma
        
        # Eşleşme bulunamadıysa None döndür
        return None

    def post(self, request):
        """
        POST isteği için Excel dosyasını işler ve kargo ücretlerini ekler
        """
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Form verilerini al
                pazar_yeri = serializer.validated_data.get('pazar_yeri')
                excel_dosya = serializer.validated_data.get('excel_dosya')
                
                # Excel dosyasını oku
                df = pd.read_excel(excel_dosya)
                
                # Desi sütununu al ve nan değerlerini temizle
                desi_values = df.iloc[:, 0].dropna().tolist()  # İlk sütun desi değerleri
                
                # Kargo firmalarını al (2. sütundan sonraki tüm sütunlar)
                kargo_firmalari = df.columns[1:].tolist()
                
                # Kargo firma adlarını temizle ve birleştir
                temiz_kargo_firmalari = {}
                for firma in kargo_firmalari:
                    # Satır sonlarını temizle ve boşlukları normalize et
                    temiz_firma = ' '.join(firma.replace('\n', ' ').split())
                    temiz_kargo_firmalari[temiz_firma] = firma
                
                # Önce seçilen pazar yerine ait tüm kargo ücretlerini sil
                DesiKgKargoUcret.objects.filter(pazar_yeri=pazar_yeri).delete()
                
                # Her bir desi değeri için
                for desi_value in desi_values:
                    # Desi değerini oluştur veya güncelle
                    desi_kg_deger, created = DesiKgDeger.objects.get_or_create(
                        pazar_yeri=pazar_yeri,
                        desi_degeri=desi_value
                    )
                    
                    # Her bir kargo firması için
                    for temiz_firma, orijinal_firma in temiz_kargo_firmalari.items():
                        # Kargo firmasını bul
                        kargo_firma = self.find_matching_kargo_firma(temiz_firma)
                        
                        # Eşleşme bulunamadıysa yeni firma oluştur
                        if not kargo_firma:
                            # Baş harfleri büyük yap
                            formatted_firma = ' '.join(word.capitalize() for word in temiz_firma.split())
                            kargo_firma = KargoFirma.objects.create(
                                firma_ismi=formatted_firma,
                                aktif=True
                            )
                        
                        # Pazar yeri - kargo firma ilişkisini oluştur
                        PazaryeriKargofirma.objects.get_or_create(
                            pazar_yeri=pazar_yeri,
                            kargo_firma=kargo_firma
                        )
                        
                        # Kargo ücretini al
                        ucret_value = df[df.iloc[:, 0] == desi_value][orijinal_firma].iloc[0]
                        
                        # Eğer değer nan ise bu kargo firması için ücret oluşturma
                        if pd.isna(ucret_value):
                            continue
                            
                        # ₺ işaretini kaldır ve virgülü noktaya çevir
                        ucret_str = str(ucret_value)
                        ucret_str = ucret_str.replace('₺', '').replace(',', '.').strip()
                        
                        try:
                            ucret = float(ucret_str)
                            
                            # Kargo ücretini oluştur
                            DesiKgKargoUcret.objects.create(
                                pazar_yeri=pazar_yeri,
                                kargo_firma=kargo_firma,
                                desi_kg_deger=desi_kg_deger,
                                ucret=ucret
                            )
                        except (ValueError, TypeError):
                            # Eğer değer sayıya çevrilemezse bu kargo firması için ücret oluşturma
                            continue
                
                return Response({
                    'message': f'{pazar_yeri.pazar_ismi} için kargo ücretleri başarıyla eklendi.',
                    'pazar_yeri': pazar_yeri.pazar_ismi,
                    'dosya_adi': excel_dosya.name,
                    'islenen_desi_sayisi': len(desi_values),
                    'islenen_kargo_firma_sayisi': len(kargo_firmalari)
                })
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KomisyonEklemeView(APIView):
    """
    Komisyon oranı ekleme endpoint'i için view
    """
    permission_classes = [IsAdminUser]
    serializer_class = KomisyonEklemeSerializer
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def get(self, request):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        serializer = self.serializer_class()
        response_data = serializer.data
        response_data['uyari_mesaji'] = (
            "Yüklenecek excel dosyası şu formatta olmalıdır:\n"
            "Kategori Ağacı 1 | Kategori Ağacı 2 | Kategori Ağacı 3 | Kategori Ağacı 4 | Komisyon Oranı (%)\n"
            "Örnek: Elektronik | Telefon | Akıllı Telefon | Android | 12.5\n\n"
            "Not: Seçtiğiniz kategori seviyesine göre Excel dosyasındaki sütun sayısı ayarlanmalıdır.\n"
            "Örneğin, kategori seviyesi 3 seçtiyseniz, Excel dosyası şu sütunları içermelidir:\n"
            "Kategori Ağacı 1 | Kategori Ağacı 2 | Kategori Ağacı 3 | Komisyon Oranı"
        )
        return Response(response_data)

    def post(self, request):
        """
        POST isteği için Excel dosyasını işler ve komisyon oranlarını ekler
        """
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Form verilerini al
                pazar_yeri = serializer.validated_data.get('pazar_yeri')
                kategori_seviyesi = serializer.validated_data.get('kategori_seviyesi')
                excel_dosya = serializer.validated_data.get('excel_dosya')
                
                # Excel dosyasını oku
                df = pd.read_excel(excel_dosya)
                
                # Sütun isimlerini kontrol et
                required_columns = ['Kategori Ağacı 1', 'Komisyon Oranı']
                if not all(col in df.columns for col in required_columns):
                    return Response(
                        {'error': 'Excel dosyası en az "Kategori Ağacı 1" ve "Komisyon Oranı" sütunlarını içermelidir.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Excel'deki sütun sayısını kontrol et
                kategori_columns = [f'Kategori Ağacı {i}' for i in range(1, kategori_seviyesi + 1)]
                if not all(col in df.columns for col in kategori_columns):
                    return Response(
                        {'error': f'Excel dosyası seçtiğiniz {kategori_seviyesi} seviye kategori için gerekli sütunları içermelidir.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Önce seçilen pazar yerine ait tüm komisyon oranlarını ve kategorileri sil
                HesaplamaKomisyonOranlari.objects.filter(pazar_yeri=pazar_yeri).delete()
                HesaplamaKategoriler.objects.filter(pazar_yeri=pazar_yeri).delete()
                
                # Yeni komisyon oranlarını ekle
                for _, row in df.iterrows():
                    # Kategori isimlerini al
                    kategori_isimleri = [row[f'Kategori Ağacı {i}'] for i in range(1, kategori_seviyesi + 1)]
                    
                    # Her seviye için kategoriyi bul veya oluştur
                    ust_kategori = None
                    kategoriler = []
                    
                    for i, kategori_ismi in enumerate(kategori_isimleri, 1):
                        # Kategoriyi bul veya oluştur
                        kategori, created = HesaplamaKategoriler.objects.get_or_create(
                            adi=kategori_ismi,
                            ust_kategori=ust_kategori,
                            seviye=i,
                            pazar_yeri=pazar_yeri
                        )
                        kategoriler.append(kategori)
                        ust_kategori = kategori
                    
                    # Komisyon oranını işle
                    komisyon_orani_str = str(row['Komisyon Oranı'])
                    # Yüzde işaretini kaldır
                    komisyon_orani_str = komisyon_orani_str.replace('%', '').strip()
                    # Virgülü noktaya çevir
                    komisyon_orani_str = komisyon_orani_str.replace(',', '.')
                    # String'i float'a çevir
                    komisyon_orani = float(komisyon_orani_str)
                    
                    # Komisyon oranını kaydet
                    komisyon_orani = HesaplamaKomisyonOranlari.objects.create(
                        pazar_yeri=pazar_yeri,
                        kategori_1=kategoriler[0],
                        kategori_2=kategoriler[1] if len(kategoriler) > 1 else None,
                        kategori_3=kategoriler[2] if len(kategoriler) > 2 else None,
                        kategori_4=kategoriler[3] if len(kategoriler) > 3 else None,
                        komisyon_orani=komisyon_orani,
                        gecerlilik_tarihi=timezone.now().date()
                    )
                
                return Response({
                    'message': f'{pazar_yeri.pazar_ismi} için komisyon oranları başarıyla eklendi.',
                    'pazar_yeri': pazar_yeri.pazar_ismi,
                    'kategori_seviyesi': kategori_seviyesi,
                    'dosya_adi': excel_dosya.name
                })
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class KomisyonOraniBulmaView(UsernameMixin, APIView):
    """
    Komisyon oranı bulma endpoint'i için view
    """
    permission_classes = [AllowAny]
    serializer_class = KomisyonOraniBulmaSerializer
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def get(self, request, username=None, format=None):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response

        serializer = self.serializer_class()
        return Response(serializer.to_representation(None))

    def post(self, request, username=None, format=None):
        """
        POST isteği için hesaplama yapar ve sonuçları döndürür
        """
        error_response = self.validate_username(username)
        if error_response:
            return error_response

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                # Email kontrolü
                email = serializer.validated_data.get('email', '').strip().lower()
                
                # Hesaplama geçmişi kontrolü ve bağlama
                if not check_and_link_calculations(request.user, email):
                    return Response(
                        {'error': 'Girdiğiniz email adresi ile giriş yaptığınız email adresi eşleşmiyor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Form verilerini al
                pazar_yeri = serializer.validated_data['pazar_yeri']
                kategori_yolu_text = serializer.validated_data['kategori_yolu']
                urun_ismi = serializer.validated_data.get('urun_ismi', 'Ürün')

                # Kategori yolunu parçala
                kategori_parcalari = [k.strip() for k in kategori_yolu_text.split('>')]

                # Komisyon oranını bul
                komisyon_orani = HesaplamaKomisyonOranlari.objects.filter(
                    pazar_yeri=pazar_yeri,
                    kategori_1__adi=kategori_parcalari[0]
                )

                if len(kategori_parcalari) > 1 and komisyon_orani.exists():
                    komisyon_orani = komisyon_orani.filter(kategori_2__adi=kategori_parcalari[1])
                if len(kategori_parcalari) > 2 and komisyon_orani.exists():
                    komisyon_orani = komisyon_orani.filter(kategori_3__adi=kategori_parcalari[2])
                if len(kategori_parcalari) > 3 and komisyon_orani.exists():
                    komisyon_orani = komisyon_orani.filter(kategori_4__adi=kategori_parcalari[3])

                komisyon_orani = komisyon_orani.first()

                if not komisyon_orani:
                    return Response(
                        {'error': f'{pazar_yeri.pazar_ismi} için seçilen kategoride komisyon oranı bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Hesaplama geçmişini kaydet
                from hesaplama.models import KomisyonOraniGecmisi
                KomisyonOraniGecmisi.objects.create(
                    kullanici=request.user if request.user.is_authenticated else None,
                    email=email,
                    pazar_yeri=pazar_yeri,
                    kategori_yolu=komisyon_orani.kategori_1,
                    komisyon_orani=komisyon_orani.komisyon_orani,
                    urun_ismi=urun_ismi
                )

                # Sonuçları döndür
                return Response({
                    'komisyon_orani': komisyon_orani.komisyon_orani,
                    'kategori_yolu': kategori_yolu_text,
                    'pazar_yeri': pazar_yeri.pazar_ismi,
                    'email': email,
                    'urun_ismi': urun_ismi
                })

            except Exception as e:
                logging.error(f"Komisyon oranı hesaplanırken hata oluştu: {str(e)}")
                return Response(
                    {'error': 'Komisyon oranı hesaplanırken bir hata oluştu.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FiyatHesaplamaView(UsernameMixin, APIView):
    """
    Fiyat hesaplama endpoint'i
    """
    permission_classes = [AllowAny]
    serializer_class = FiyatHesaplamaSerializer

    def validate_email(self, email):
        """
        Email adresinin sistemde kayıtlı olup olmadığını kontrol eder
        """
        if not email:
            return False
        return get_user_model().objects.filter(email=email).exists()

    def get(self, request, username=None, format=None):
        # Validate username from URL
        validation_response = self.validate_username(username)
        if validation_response:
            return validation_response

        # Get query parameters
        email = request.query_params.get('email')
        pazar_yeri = request.query_params.get('pazar_yeri')
        
        if email and not self.validate_email(email):
            return Response(
                {'error': 'Bu email adresi sistemde kayıtlı değil.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create context with pazar_yeri if provided
        context = {'request': request}
        if pazar_yeri:
            context['pazar_yeri_id'] = pazar_yeri
            
        serializer = self.serializer_class(context=context)
        return Response(serializer.to_representation({}))

    def post(self, request, username=None, format=None):
        # Validate username from URL
        validation_response = self.validate_username(username)
        if validation_response:
            return validation_response

        email = request.data.get('email')
        if email and not self.validate_email(email):
            return Response(
                {'error': 'Bu email adresi sistemde kayıtlı değil.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        pazar_yeri = data['pazar_yeri']
        urun_maliyeti = data['urun_maliyeti']
        paketleme_bedeli = data['paketleme_bedeli']
        urun_desi_kg = data['urun_desi_kg']
        kargo_firma = data['kargo_firma']
        kategori_yolu = data['kategori_yolu']
        kar_orani = data['kar_orani']
        kdv_orani = data['kdv_orani']

        # Get shipping cost
        try:
            desi_kg_deger = DesiKgDeger.objects.get(
                pazar_yeri=pazar_yeri,
                desi_degeri__gte=urun_desi_kg
            )
            kargo_ucret = DesiKgKargoUcret.objects.get(
                desi_kg_deger=desi_kg_deger,
                kargo_firma=kargo_firma
            )
            kargo_bedeli = kargo_ucret.ucret
        except (DesiKgDeger.DoesNotExist, DesiKgKargoUcret.DoesNotExist):
            return Response(
                {'error': 'Bu desi/kg değeri için kargo ücreti bulunamadı.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate total cost
        toplam_maliyet = urun_maliyeti + paketleme_bedeli + kargo_bedeli

        # Get commission rate
        try:
            komisyon_orani = HesaplamaKomisyonOranlari.objects.get(
                kategori=kategori_yolu
            ).komisyon_orani
        except HesaplamaKomisyonOranlari.DoesNotExist:
            return Response(
                {'error': 'Bu kategori için komisyon oranı bulunamadı.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate amounts
        komisyon_tutari = (toplam_maliyet * Decimal(str(komisyon_orani))) / Decimal('100')
        kar_tutari = (toplam_maliyet * Decimal(str(kar_orani))) / Decimal('100')
        kdv_tutari = ((toplam_maliyet + komisyon_tutari + kar_tutari) * Decimal(str(kdv_orani))) / Decimal('100')
        satis_fiyati = toplam_maliyet + komisyon_tutari + kar_tutari + kdv_tutari

        # Build category path
        kategori_yolu_string = []
        current = kategori_yolu
        while current:
            kategori_yolu_string.insert(0, current.ad)
            current = current.ust_kategori
        kategori_yolu_string = ' > '.join(kategori_yolu_string)

        # Save calculation history if email is provided
        if email:
            user = get_user_model().objects.get(email=email)
            KargoHesaplamaGecmisi.objects.create(
                user=user,
                pazar_yeri=pazar_yeri,
                kargo_firma=kargo_firma,
                urun_desi_kg=urun_desi_kg,
                kargo_ucreti=kargo_bedeli
            )

        response_data = {
            'urun_maliyeti': urun_maliyeti,
            'paketleme_bedeli': paketleme_bedeli,
            'kargo_bedeli': kargo_bedeli,
            'toplam_maliyet': toplam_maliyet,
            'komisyon_orani': komisyon_orani,
            'komisyon_tutari': komisyon_tutari,
            'kar_orani': kar_orani,
            'kar_tutari': kar_tutari,
            'kdv_orani': kdv_orani,
            'kdv_tutari': kdv_tutari,
            'satis_fiyati': satis_fiyati,
            'kategori_yolu': kategori_yolu_string
        }

        return Response(response_data)

class DesiKgHesaplamaView(APIView):
    """
    Desi/Kg hesaplama endpoint'i
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DesiKgHesaplamaSerializer

    def get(self, request, username):
        serializer = self.serializer_class()
        return Response(serializer.to_representation(None))

    def post(self, request, username):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Email kontrolü
            email = serializer.validated_data['email']
            if email.lower() != request.user.email.lower():
                return Response(
                    {'error': 'Girdiğiniz email adresi ile giriş yaptığınız email adresi eşleşmiyor.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            en = serializer.validated_data['en']
            boy = serializer.validated_data['boy']
            yukseklik = serializer.validated_data['yukseklik']
            net_agirlik = serializer.validated_data.get('net_agirlik', 0)

            # Desi hesaplama
            desi = (en * boy * yukseklik) / 3000
            
            # Desi değerini net ağırlığa böl ve yukarı yuvarla
            if net_agirlik > 0:
                desi_kg = math.ceil(desi / net_agirlik)
            else:
                desi_kg = math.ceil(desi)

            # Hesaplama geçmişini kaydet
            from hesaplama.models import HesaplamaDesiKgGecmisi
            HesaplamaDesiKgGecmisi.objects.create(
                kullanici=request.user,
                email=request.user.email,
                urun_ismi=serializer.validated_data.get('urun_ismi', 'Ürün'),
                en=en,
                boy=boy,
                yukseklik=yukseklik,
                net_agirlik=net_agirlik,
                desi_kg=desi_kg
            )

            return Response({
                'email': request.user.email,
                'urun_ismi': serializer.validated_data.get('urun_ismi', 'Ürün'),
                'desi': desi,
                'net_agirlik': net_agirlik,
                'kullanilacak_deger': desi_kg
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MarketplacePriceCalculationView(UsernameMixin, APIView):
    """
    Pazar yeri satış fiyatı hesaplama endpoint'i için view
    """
    permission_classes = [AllowAny]
    serializer_class = MarketplacePriceCalculationSerializer
    renderer_classes = [renderers.JSONRenderer, renderers.BrowsableAPIRenderer]

    def validate_email(self, email):
        """
        Email adresinin sistemde kayıtlı olup olmadığını kontrol eder
        """
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            return True, None  # Email kayıtlı ise hesaplama yapılabilir
        return True, None  # Email kayıtlı değilse de hesaplama yapılabilir

    def get(self, request, username=None, format=None):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        serializer = self.serializer_class()
        return Response(serializer.to_representation(None))

    def post(self, request, username=None, format=None):
        """
        POST isteği için hesaplama yapar ve sonuçları döndürür
        """
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            try:
                # Email kontrolü
                email = serializer.validated_data.get('email', '').strip().lower()
                
                # Hesaplama geçmişi kontrolü ve bağlama
                if not check_and_link_calculations(request.user, email):
                    return Response(
                        {'error': 'Girdiğiniz email adresi ile giriş yaptığınız email adresi eşleşmiyor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Form verilerini al
                pazar_yeri = serializer.validated_data['pazar_yeri']
                urun_maliyeti = serializer.validated_data['urun_maliyeti']
                paketleme_bedeli = serializer.validated_data['paketleme_bedeli']
                urun_desi_kg = serializer.validated_data['urun_desi_kg']
                kargo_firma = serializer.validated_data['kargo_firma']
                komisyon_orani = serializer.validated_data['komisyon_orani']
                kar_orani = serializer.validated_data['kar_orani']
                kdv_orani = serializer.validated_data['kdv_orani']
                
                # Hizmet bedelini belirle
                if pazar_yeri.pazar_ismi == "Trendyol":
                    hizmet_bedeli = Decimal('8.49')
                elif pazar_yeri.pazar_ismi == "Hepsiburada":
                    hizmet_bedeli = Decimal('9.5')
                else:
                    hizmet_bedeli = Decimal('0')
                
                # Kargo ücretini bul
                desi_kg_yuvarlama = math.ceil(urun_desi_kg)
                
                # Pazar yeri ve kargo firma ilişkisini kontrol et
                if not PazaryeriKargofirma.objects.filter(pazar_yeri=pazar_yeri, kargo_firma=kargo_firma).exists():
                    return Response(
                        {'error': f'{kargo_firma.firma_ismi} {pazar_yeri.pazar_ismi} için hizmet vermemektedir.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Desi/Kg değerini bul
                desi_kg_deger = DesiKgDeger.objects.filter(
                    pazar_yeri=pazar_yeri,
                    desi_degeri=desi_kg_yuvarlama
                ).first()
                
                if not desi_kg_deger:
                    return Response(
                        {'error': f'{pazar_yeri.pazar_ismi} için {desi_kg_yuvarlama} desi/kg değerinde tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Kargo ücretini bul
                kargo_ucret = DesiKgKargoUcret.objects.filter(
                    pazar_yeri=pazar_yeri,
                    kargo_firma=kargo_firma,
                    desi_kg_deger=desi_kg_deger
                ).first()
                
                if not kargo_ucret:
                    return Response(
                        {'error': f'{pazar_yeri.pazar_ismi} - {kargo_firma.firma_ismi} için {desi_kg_yuvarlama} desi/kg değerinde tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Hesaplamaları yap
                tam_kisim = (urun_maliyeti + kargo_ucret.ucret + paketleme_bedeli + hizmet_bedeli) * Decimal('100')
                stopaj_orani = Decimal('1')
                yuzde_kisim = Decimal('100') - (komisyon_orani + kar_orani + stopaj_orani)
                satis_fiyati = tam_kisim / yuzde_kisim
                
                komisyon_bedeli = satis_fiyati * komisyon_orani / Decimal('100')
                kar_bedeli = satis_fiyati * kar_orani / Decimal('100')
                stopaj_bedeli = satis_fiyati * stopaj_orani / Decimal('100')
                kdv_dahil_satis_fiyati = satis_fiyati + (satis_fiyati * kdv_orani / Decimal('100'))

                # Hesaplama geçmişini kaydet
                from hesaplama.models import FiyatHesaplamaGecmisi
                FiyatHesaplamaGecmisi.objects.create(
                    kullanici=request.user if request.user.is_authenticated else None,
                    email=email,
                    urun_ismi=serializer.validated_data.get('urun_ismi', "Ürün"),
                    pazar_yeri=pazar_yeri,
                    urun_maliyeti=urun_maliyeti,
                    paketleme_bedeli=paketleme_bedeli,
                    hizmet_bedeli=hizmet_bedeli,
                    urun_desi_kg=urun_desi_kg,
                    kargo_firma=kargo_firma,
                    kargo_ucreti=kargo_ucret.ucret,
                    komisyon_orani=komisyon_orani,
                    stopaj_orani=stopaj_orani,
                    stopaj_bedeli=stopaj_bedeli,
                    satis_fiyati=satis_fiyati,
                    kdv_dahil_satis_fiyati=kdv_dahil_satis_fiyati
                )
                
                # Sonuçları döndür
                result = {
                    'mail': email,
                    'urun_maliyeti': float(urun_maliyeti),
                    'paketleme_bedeli': float(paketleme_bedeli),
                    'pazar_yeri': pazar_yeri.pazar_ismi,
                    'hizmet_bedeli': float(hizmet_bedeli),
                    'urun_desi_kg': float(urun_desi_kg),
                    'kargo_ucreti': float(kargo_ucret.ucret),
                    'kategori_komisyon_orani': float(komisyon_orani),
                    'stopaj_orani': float(stopaj_orani),
                    'hesaplanan_stopaj_bedeli': float(stopaj_bedeli),
                    'satis_fiyati': float(satis_fiyati),
                    'kdv_dahil_satis_fiyati': float(kdv_dahil_satis_fiyati)
                }
                
                return Response(result)
                
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 