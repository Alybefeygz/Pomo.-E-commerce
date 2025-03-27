from rest_framework import viewsets, status, filters
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from hesaplama.models import KargoFirma, DesiKgDeger, DesiKgKargoUcret, Kategori, AltKategori, UrunGrubu, KomisyonOrani, Hesaplamalar, FiyatBelirleme
from .serializers import (
    KargoFirmaSerializer, DesiKgDegerSerializer, DesiKgKargoUcretSerializer, KargoUcretHesaplamaSerializer,
    KategoriSerializer, AltKategoriSerializer, UrunGrubuSerializer, KomisyonOraniSerializer,
    KategoriKomisyonBulmaSerializer, SatisFiyatBelirlemeSerializer, UserHesaplamalarSerializer, EksikHesaplamaSerializer
)
from .permissions import IsSuperUserOrReadOnly
import math
from decimal import Decimal
from rest_framework import serializers
import logging
from rest_framework import renderers

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
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

class KargoFirmaViewSet(viewsets.ModelViewSet):
    """
    Kargo firmalarını listeler, oluşturur, günceller ve siler.
    """
    queryset = KargoFirma.objects.all()
    serializer_class = KargoFirmaSerializer
    permission_classes = [IsAdminUser]

class DesiKgDegerViewSet(viewsets.ModelViewSet):
    """
    Desi-Kg değerlerini listeler, oluşturur, günceller ve siler.
    """
    queryset = DesiKgDeger.objects.all().order_by('desi_degeri')
    serializer_class = DesiKgDegerSerializer
    permission_classes = [IsAdminUser]

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
        - kargo_firma parametresi ile kargo firma ID'sine göre
        - desi_kg_deger parametresi ile desi/kg değerine göre
        """
        queryset = DesiKgKargoUcret.objects.all()
        
        # URL parametrelerini al
        kargo_firma_id = self.request.query_params.get('kargo_firma')
        desi_kg_deger_id = self.request.query_params.get('desi_kg_deger')
        
        # Kargo firma ID'sine göre filtrele
        if kargo_firma_id:
            queryset = queryset.filter(kargo_firma_id=kargo_firma_id)
            
        # Desi/Kg değerine göre filtrele
        if desi_kg_deger_id:
            queryset = queryset.filter(desi_kg_deger_id=desi_kg_deger_id)
            
        return queryset

class KargoUcretHesaplamaView(UsernameMixin, APIView):
    """
    Kargo ücretini hesaplamak için API view.
    Kullanıcıdan email, en, boy, yükseklik, net ağırlık ve kargo firması bilgilerini alır.
    """
    serializer_class = KargoUcretHesaplamaSerializer
    
    def get(self, request, username, format=None):
        # Kargo firmalarını al
        kargo_firmalar = KargoFirma.objects.all()
        kargo_firma_secenekleri = {firma.id: firma.firma_ismi for firma in kargo_firmalar}
        
        # Context'i hazırla
        context = {'kargo_firma_secenekleri': kargo_firma_secenekleri}
        
        # Eğer kullanıcı giriş yapmışsa, email adresini ekle
        if request.user.is_authenticated:
            context['email'] = request.user.email
            
        # Serializer oluştur
        serializer = self.serializer_class(context=context)
        
        # Eğer kullanıcı giriş yapmışsa, email alanını önceden doldur
        data = serializer.data
        if request.user.is_authenticated:
            data['email'] = request.user.email
            
        return Response(data)
    
    def post(self, request, username, format=None):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            # Email validasyonu
            submitted_email = serializer.validated_data.get('email', '').strip().lower()
            
            # Eğer kullanıcı giriş yapmışsa email kontrolü yap
            if request.user.is_authenticated:
                user_email = request.user.email.strip().lower()
                if submitted_email != user_email:
                    return Response(
                        {'error': 'Giriş yaptığınız hesabın email adresi ile form üzerindeki email adresi eşleşmiyor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Kullanıcı giriş yapmamışsa, girilen email'in sistemde kayıtlı olup olmadığını kontrol et
                User = get_user_model()
                if User.objects.filter(email__iexact=submitted_email).exists():
                    return Response(
                        {'error': 'Bu email adresi sistemde kayıtlıdır. Lütfen giriş yapın veya başka bir email adresi kullanın.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            en = serializer.validated_data.get('en')
            boy = serializer.validated_data.get('boy')
            yukseklik = serializer.validated_data.get('yukseklik')
            net_agirlik = serializer.validated_data.get('net_agirlik')
            kargo_firma_id = serializer.validated_data.get('kargo_firma')
            
            # Desi hesaplama
            desi = (en * boy * yukseklik) / 3000
            
            # Desi/Kg hesaplama ve tam sayıya yuvarlama
            desi_kg = max(desi, net_agirlik)
            desi_kg_yuvarlama = math.ceil(desi_kg)
            
            try:
                # Kargo firmasını bul
                kargo_firma = KargoFirma.objects.get(id=kargo_firma_id)
                
                # Desi/Kg değerini bul
                desi_kg_deger = DesiKgDeger.objects.filter(desi_degeri=desi_kg_yuvarlama).first()
                
                if not desi_kg_deger:
                    return Response(
                        {'error': f'Desi/Kg değeri {desi_kg_yuvarlama} için tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Kargo ücretini bul
                kargo_ucret = DesiKgKargoUcret.objects.filter(
                    kargo_firma=kargo_firma,
                    desi_kg_deger=desi_kg_deger
                ).first()
                
                if not kargo_ucret:
                    return Response(
                        {'error': f'{kargo_firma.firma_ismi} için {desi_kg_yuvarlama} desi/kg değerinde tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Sonuçları döndür
                result = {
                    'email': submitted_email,  # Normalize edilmiş email'i dön
                    'en': en,
                    'boy': boy,
                    'yukseklik': yukseklik,
                    'net_agirlik': net_agirlik,
                    'desi': desi,
                    'desi_kg': desi_kg_yuvarlama,
                    'kargo_firma_ismi': kargo_firma.firma_ismi,
                    'kargo_ucreti': kargo_ucret.fiyat
                }
                
                return Response(result)
                
            except KargoFirma.DoesNotExist:
                return Response(
                    {'error': 'Belirtilen kargo firması bulunamadı.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

class KategoriKomisyonBulmaView(UsernameMixin, APIView):
    """
    Seçilen ürün grubunun komisyon oranını bulan API view.
    Kullanıcının hierarşik olarak kategori, alt kategori ve ürün grubu seçmesini sağlar.
    """
    serializer_class = KategoriKomisyonBulmaSerializer
    
    def get(self, request, username, format=None):
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        # Context'i hazırla
        context = {}
        
        # Eğer kullanıcı giriş yapmışsa, email adresini ekle
        if request.user.is_authenticated:
            context['email'] = request.user.email
            
        # Boş serializer oluştur
        serializer = self.serializer_class(context=context)
        
        # Eğer kullanıcı giriş yapmışsa, email alanını önceden doldur
        data = serializer.data
        if request.user.is_authenticated:
            data['email'] = request.user.email
        
        # Kategorileri al
        kategoriler = Kategori.objects.all().order_by('kategori_adi')
        kategori_data = KategoriSerializer(kategoriler, many=True).data
        
        # Kategori ID parametresi varsa, ilgili alt kategorileri getir
        kategori_id = request.query_params.get('kategori_id')
        if kategori_id:
            alt_kategoriler = AltKategori.objects.filter(kategori_id=kategori_id).order_by('alt_kategori_adi')
            alt_kategori_data = AltKategoriSerializer(alt_kategoriler, many=True).data
            data['alt_kategoriler'] = alt_kategori_data
        
        # Alt kategori ID parametresi varsa, ilgili ürün gruplarını getir
        alt_kategori_id = request.query_params.get('alt_kategori_id')
        if alt_kategori_id:
            urun_gruplari = UrunGrubu.objects.filter(alt_kategori_id=alt_kategori_id).order_by('urun_grubu_adi')
            urun_grubu_data = UrunGrubuSerializer(urun_gruplari, many=True).data
            data['urun_gruplari'] = urun_grubu_data
        
        # Tüm kategorileri ekle
        data['kategoriler'] = kategori_data
            
        return Response(data)
    
    def post(self, request, username, format=None):
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            # Email validasyonu
            submitted_email = serializer.validated_data.get('email', '').strip().lower()
            
            # Eğer kullanıcı giriş yapmışsa email kontrolü yap
            if request.user.is_authenticated:
                user_email = request.user.email.strip().lower()
                if submitted_email != user_email:
                    return Response(
                        {'error': 'Giriş yaptığınız hesabın email adresi ile form üzerindeki email adresi eşleşmiyor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Kullanıcı giriş yapmamışsa, girilen email'in sistemde kayıtlı olup olmadığını kontrol et
                User = get_user_model()
                if User.objects.filter(email__iexact=submitted_email).exists():
                    return Response(
                        {'error': 'Bu email adresi sistemde kayıtlıdır. Lütfen giriş yapın veya başka bir email adresi kullanın.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Ürün grubu alanını kontrol et
            urun_grubu = serializer.validated_data.get('urun_grubu')
            if not urun_grubu:
                return Response(
                    {'error': 'Lütfen bir ürün grubu seçiniz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # Seçilen ürün grubuna ait komisyon oranını bul
                komisyon_orani = KomisyonOrani.objects.select_related(
                    'urun_grubu__alt_kategori__kategori'
                ).filter(
                    urun_grubu=urun_grubu
                ).first()
                
                if komisyon_orani:
                    # Serializer'ı komisyon oranı instance'ı ile oluştur ve email'i context'e ekle
                    response_serializer = self.serializer_class(
                        komisyon_orani,
                        context={'email': submitted_email}
                    )
                    return Response(response_serializer.data)
                else:
                    return Response(
                        {'error': f'Seçilen ürün grubu için komisyon oranı bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SatisFiyatBelirlemeView(UsernameMixin, APIView):
    """
    Satış fiyatını belirlemek için API view.
    """
    serializer_class = SatisFiyatBelirlemeSerializer
    
    def get(self, request, username, format=None):
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response
            
        # Kargo firmalarını al - string ID'leri kullanarak dictionary oluştur
        kargo_firmalar = KargoFirma.objects.all()
        kargo_firma_secenekleri = {str(firma.id): firma.firma_ismi for firma in kargo_firmalar}
        
        # Context'i hazırla
        context = {'kargo_firma_secenekleri': kargo_firma_secenekleri}
        
        # Eğer kullanıcı giriş yapmışsa, email adresini ekle
        if request.user.is_authenticated:
            context['email'] = request.user.email
            
        # Boş serializer oluştur
        serializer = self.serializer_class(context=context)
        
        # Eğer kullanıcı giriş yapmışsa, email alanını önceden doldur
        data = serializer.data
        if request.user.is_authenticated:
            data['email'] = request.user.email
            
        # Kategorileri al
        kategoriler = Kategori.objects.all().order_by('kategori_adi')
        kategori_data = KategoriSerializer(kategoriler, many=True).data
        
        # Kategori ID parametresi varsa, ilgili alt kategorileri getir
        kategori_id = request.query_params.get('kategori_id')
        if kategori_id:
            alt_kategoriler = AltKategori.objects.filter(kategori_id=kategori_id).order_by('alt_kategori_adi')
            alt_kategori_data = AltKategoriSerializer(alt_kategoriler, many=True).data
            data['alt_kategoriler'] = alt_kategori_data
        
        # Alt kategori ID parametresi varsa, ilgili ürün gruplarını getir
        alt_kategori_id = request.query_params.get('alt_kategori_id')
        if alt_kategori_id:
            urun_gruplari = UrunGrubu.objects.filter(alt_kategori_id=alt_kategori_id).order_by('urun_grubu_adi')
            urun_grubu_data = UrunGrubuSerializer(urun_gruplari, many=True).data
            data['urun_gruplari'] = urun_grubu_data
        
        # Tüm kategorileri ekle
        data['kategoriler'] = kategori_data
        
        # Kargo firma seçeneklerini doğrudan ekle
        data['kargo_firma_secenekleri'] = kargo_firma_secenekleri
            
        return Response(data)
    
    def post(self, request, username, format=None):
        # Validate username
        error_response = self.validate_username(username)
        if error_response:
            return error_response
        
        # Log request data for debugging
        logger = logging.getLogger(__name__)
        logger.info(f"Request data: {request.data}")
        
        # Get kargo firmalar for choices before serializer validation
        kargo_firmalar = KargoFirma.objects.all()
        kargo_firma_secenekleri = {str(firma.id): firma.firma_ismi for firma in kargo_firmalar}
        
        # Create context with kargo_firma_secenekleri
        context = {'kargo_firma_secenekleri': kargo_firma_secenekleri}
        
        # Log the choices we're about to use
        logger.info(f"Kargo firma choices for validation: {kargo_firma_secenekleri}")
        
        # Create serializer with context
        serializer = self.serializer_class(data=request.data, context=context)
            
        if serializer.is_valid():
            # Email validasyonu
            submitted_email = serializer.validated_data.get('email', '').strip().lower()
            
            # Log validated data for debugging
            logger.info(f"Validated data: {serializer.validated_data}")
            
            # Eğer kullanıcı giriş yapmışsa email kontrolü yap
            if request.user.is_authenticated:
                user_email = request.user.email.strip().lower()
                if submitted_email != user_email:
                    return Response(
                        {'error': 'Giriş yaptığınız hesabın email adresi ile form üzerindeki email adresi eşleşmiyor.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Kullanıcı giriş yapmamışsa, girilen email'in sistemde kayıtlı olup olmadığını kontrol et
                User = get_user_model()
                if User.objects.filter(email__iexact=submitted_email).exists():
                    return Response(
                        {'error': 'Bu email adresi sistemde kayıtlıdır. Lütfen giriş yapın veya başka bir email adresi kullanın.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            data = serializer.validated_data
            
            # Kategori, alt kategori ve ürün grubu validasyonu
            kategori = data.get('kategori')
            alt_kategori = data.get('alt_kategori')
            urun_grubu = data.get('urun_grubu')
            
            if not urun_grubu:
                return Response(
                    {'error': 'Lütfen bir ürün grubu seçiniz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Alt kategori ve kategori tutarlılık kontrolü
            if alt_kategori and urun_grubu.alt_kategori != alt_kategori:
                return Response(
                    {'error': 'Seçilen ürün grubu, seçilen alt kategori ile uyumlu değil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if kategori and (not alt_kategori or alt_kategori.kategori != kategori):
                return Response(
                    {'error': 'Seçilen alt kategori, seçilen kategori ile uyumlu değil.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Calculate desi
            desi = (data['en'] * data['boy'] * data['yukseklik']) / 3000
            
            # Calculate desi/kg and round up
            desi_kg = max(desi, data['net_agirlik'])
            desi_kg_yuvarlama = math.ceil(desi_kg)
            
            try:
                # Get kargo firması
                kargo_firma_id = data['kargo_firma']
                # String veya integer olabilir, integer'a dönüştür
                kargo_firma_id = int(kargo_firma_id)
                
                kargo_firma = KargoFirma.objects.get(id=kargo_firma_id)
                
                # Get desi/kg değeri
                desi_kg_deger = DesiKgDeger.objects.filter(desi_degeri=desi_kg_yuvarlama).first()
                
                if not desi_kg_deger:
                    return Response(
                        {'error': f'Desi/Kg değeri {desi_kg_yuvarlama} için tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Get kargo ücreti
                kargo_ucret = DesiKgKargoUcret.objects.filter(
                    kargo_firma=kargo_firma,
                    desi_kg_deger=desi_kg_deger
                ).first()
                
                if not kargo_ucret:
                    return Response(
                        {'error': f'{kargo_firma.firma_ismi} için {desi_kg_yuvarlama} desi/kg değerinde tarife bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Get komisyon oranı
                komisyon_orani = KomisyonOrani.objects.filter(urun_grubu=urun_grubu).first()
                
                if not komisyon_orani:
                    return Response(
                        {'error': 'Seçilen ürün grubu için komisyon oranı bulunamadı.'},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                # Trendyol hizmet bedeli ve stopaj değerlerini ayarla
                trendyol_hizmet_bedeli = Decimal('8.49')
                stopaj_degeri = Decimal('1.00')  # %1
                
                # Calculate total cost (1. madde)
                toplam_maliyet = (
                    data['urun_maliyeti'] +
                    data['urun_paketleme_maliyeti'] +
                    kargo_ucret.fiyat +
                    trendyol_hizmet_bedeli
                )
                
                # 2. madde - oranları topla ve 100'den çıkar
                toplam_oranlar = stopaj_degeri + komisyon_orani.komisyon_orani + data['istenilen_kar_orani']
                kalan_oran = Decimal('100') - toplam_oranlar
                
                # Satış fiyatı = toplam_maliyet * 100 / kalan_oran
                satis_fiyati_kdv_haric = (toplam_maliyet * Decimal('100')) / kalan_oran
                
                # Calculate individual amounts based on the sales price
                stopaj_tutari = (satis_fiyati_kdv_haric * stopaj_degeri) / Decimal('100')
                komisyon_tutari = (satis_fiyati_kdv_haric * komisyon_orani.komisyon_orani) / Decimal('100')
                kar_tutari = (satis_fiyati_kdv_haric * data['istenilen_kar_orani']) / Decimal('100')
                
                # Calculate price with VAT
                satis_fiyati_kdv_dahil = satis_fiyati_kdv_haric * (Decimal('1') + data['kdv_orani'] / Decimal('100'))
                
                # Create Hesaplamalar record
                hesaplama = Hesaplamalar.objects.create(
                    kullanici=request.user if request.user.is_authenticated else None,
                    email=submitted_email,
                    toplam_fiyat=satis_fiyati_kdv_dahil
                )
                
                # Create FiyatBelirleme record
                fiyat_belirleme = FiyatBelirleme.objects.create(
                    hesaplama=hesaplama,
                    urun_ismi=data['urun_ismi'],
                    urun_maliyeti=data['urun_maliyeti'],
                    paketleme_maliyeti=data['urun_paketleme_maliyeti'],
                    trendyol_hizmet_bedeli=trendyol_hizmet_bedeli,
                    kargo_firmasi=kargo_firma.firma_ismi,
                    kargo_ucreti=kargo_ucret.fiyat,
                    stopaj_degeri=stopaj_degeri,
                    desi_kg_degeri=desi_kg_yuvarlama,
                    urun_kategorisi=f"{urun_grubu.alt_kategori.kategori.kategori_adi} > {urun_grubu.alt_kategori.alt_kategori_adi} > {urun_grubu.urun_grubu_adi}",
                    komisyon_orani=komisyon_orani.komisyon_orani,
                    komisyon_tutari=komisyon_tutari,
                    kdv_orani=data['kdv_orani'],
                    kar_orani=data['istenilen_kar_orani'],
                    kar_tutari=kar_tutari,
                    satis_fiyati_kdv_haric=satis_fiyati_kdv_haric,
                    satis_fiyati_kdv_dahil=satis_fiyati_kdv_dahil
                )
                
                # Return the calculation results
                result = {
                    'hesaplama_id': hesaplama.hesaplama_id,
                    'email': submitted_email,  # Add email to response
                    'urun_id': fiyat_belirleme.urun_id,
                    'urun_ismi': fiyat_belirleme.urun_ismi,
                    'urun_maliyeti': float(data['urun_maliyeti']),
                    'Paketleme Maliyeti': float(data['urun_paketleme_maliyeti']),
                    'Trendyol Hizmet Bedeli': float(trendyol_hizmet_bedeli),
                    'Desi/Kg Değeri': desi_kg_yuvarlama,
                    'Kargo Firması': kargo_firma.firma_ismi,
                    'Kargo Ücreti': float(kargo_ucret.fiyat),
                    'Stopaj': float(stopaj_degeri),
                    'Stopaj Ücreti': float(stopaj_tutari),
                    'Kategori': urun_grubu.alt_kategori.kategori.kategori_adi,
                    'Alt Kategori': urun_grubu.alt_kategori.alt_kategori_adi,
                    'Ürün Grubu': urun_grubu.urun_grubu_adi,
                    'Ürün Kategorisi Komisyon Oranı': float(komisyon_orani.komisyon_orani),
                    'Ürün Kategorisi Komisyon Tutarı': float(komisyon_tutari),
                    'Kar Oranı': float(data['istenilen_kar_orani']),
                    'Kar Tutarı': float(kar_tutari),
                    'Belirlenen KDV Tutarı': float(data['kdv_orani']),
                    'KDV fiyatı': float(satis_fiyati_kdv_dahil - satis_fiyati_kdv_haric),
                    'Satış Fiyatı(KDV Dahil değil)': float(satis_fiyati_kdv_haric),
                    'Satış Fiyatı(KDV Dahil)': float(satis_fiyati_kdv_dahil)
                }
                
                return Response(result)
                
            except KargoFirma.DoesNotExist:
                return Response(
                    {'error': 'Belirtilen kargo firması bulunamadı.'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Log validation errors
            logger.error(f"Validation errors: {serializer.errors}")
            
            # Check specifically for kargo_firma error
            if 'kargo_firma' in serializer.errors:
                logger.error(f"Kargo firma error: {serializer.errors['kargo_firma']}")
                logger.error(f"Kargo firma value in request: {request.data.get('kargo_firma', 'Not provided')}")
                logger.error(f"Kargo firma choices: {serializer.fields['kargo_firma'].choices}")
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserHesaplamalarSerializer(serializers.Serializer):
    username = serializers.ChoiceField(
        choices=[],
        required=False,
        allow_null=True,
        style={'base_template': 'select.html'},
        help_text="Kullanıcı seçerek hesaplamalarını görüntüleyebilirsiniz"
    )
    show_guest = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Misafir kullanıcıların hesaplamalarını göster"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        User = get_user_model()
        users = User.objects.all()
        self.fields['username'].choices = [(None, '-- Tüm Kullanıcılar --')] + [
            (user.username, f"Kullanıcı: {user.username}") 
            for user in users
        ]

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