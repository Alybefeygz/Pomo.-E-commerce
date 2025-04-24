from rest_framework import serializers
from hesaplama.models import (
    Pazaryeri, KargoFirma, DesiKgDeger, DesiKgKargoUcret, PazaryeriKargofirma,
    Kategori, AltKategori, UrunGrubu, KomisyonOrani, HesaplamaKategoriler, HesaplamaKomisyonOranlari,
    KategoriYolu, Hesaplamalar, KargoHesaplamaGecmisi, HesaplamaKategoriSeviyeleri
)
from decimal import Decimal, InvalidOperation
from django.contrib.auth import get_user_model

class PazaryeriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pazaryeri
        fields = ['id', 'pazar_ismi', 'aktif']

class KargoFirmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = KargoFirma
        fields = ['id', 'firma_ismi', 'logo', 'aktif']

class DesiKgDegerSerializer(serializers.ModelSerializer):
    pazar_yeri_ismi = serializers.CharField(source='pazar_yeri.pazar_ismi', read_only=True)

    class Meta:
        model = DesiKgDeger
        fields = ['id', 'pazar_yeri', 'pazar_yeri_ismi', 'desi_degeri']

class DesiKgKargoUcretSerializer(serializers.ModelSerializer):
    pazar_yeri_ismi = serializers.CharField(source='pazar_yeri.pazar_ismi', read_only=True)
    kargo_firma_ismi = serializers.CharField(source='kargo_firma.firma_ismi', read_only=True)
    desi_kg_degeri = serializers.FloatField(source='desi_kg_deger.desi_degeri', read_only=True)

    class Meta:
        model = DesiKgKargoUcret
        fields = ['id', 'pazar_yeri', 'pazar_yeri_ismi', 'kargo_firma', 'kargo_firma_ismi', 
                 'desi_kg_deger', 'desi_kg_degeri', 'ucret']

class PazaryeriKargofirmaSerializer(serializers.ModelSerializer):
    pazar_yeri_ismi = serializers.CharField(source='pazar_yeri.pazar_ismi', read_only=True)
    kargo_firma_ismi = serializers.CharField(source='kargo_firma.firma_ismi', read_only=True)

    class Meta:
        model = PazaryeriKargofirma
        fields = ['id', 'pazar_yeri', 'pazar_yeri_ismi', 'kargo_firma', 'kargo_firma_ismi']

class KargoUcretHesaplamaSerializer(serializers.Serializer):
    """
    Kargo ücreti hesaplama için serializer
    """
    email = serializers.EmailField(required=False)
    pazar_yeri = serializers.PrimaryKeyRelatedField(queryset=Pazaryeri.objects.filter(aktif=True))
    kargo_firma = serializers.PrimaryKeyRelatedField(queryset=KargoFirma.objects.filter(aktif=True))
    desi_kg_degeri = serializers.DecimalField(max_digits=10, decimal_places=2)

    def to_representation(self, instance):
        """
        Form verilerini ve seçenekleri döndürür
        """
        data = {
            'pazar_yerleri': [
                {'id': pazar_yeri.id, 'pazar_ismi': pazar_yeri.pazar_ismi}
                for pazar_yeri in Pazaryeri.objects.filter(aktif=True)
            ],
            'kargo_firmalari': [
                {'id': kargo_firma.id, 'firma_ismi': kargo_firma.firma_ismi}
                for kargo_firma in KargoFirma.objects.filter(aktif=True)
            ]
        }
        return data

# Kategori ve komisyon oranları için serializer'lar
class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = ['id', 'kategori_adi']

class AltKategoriSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer(read_only=True)
    kategori_id = serializers.PrimaryKeyRelatedField(
        queryset=Kategori.objects.all(), 
        source='kategori',
        write_only=True
    )
    
    class Meta:
        model = AltKategori
        fields = ['id', 'kategori', 'kategori_id', 'alt_kategori_adi']

class UrunGrubuSerializer(serializers.ModelSerializer):
    alt_kategori = AltKategoriSerializer(read_only=True)
    alt_kategori_id = serializers.PrimaryKeyRelatedField(
        queryset=AltKategori.objects.all(), 
        source='alt_kategori',
        write_only=True
    )
    
    class Meta:
        model = UrunGrubu
        fields = ['id', 'alt_kategori', 'alt_kategori_id', 'urun_grubu_adi']

class KomisyonOraniSerializer(serializers.ModelSerializer):
    class Meta:
        model = KomisyonOrani
        fields = ['id', 'urun_grubu', 'pazar_yeri', 'komisyon_orani', 'created_at', 'updated_at']

class KategoriKomisyonBulmaSerializer(serializers.Serializer):
    """
    Seçilen pazar yerine ait kategorilerin komisyon oranını bulan serializer.
    """
    email = serializers.EmailField(required=False)
    pazar_yeri = serializers.PrimaryKeyRelatedField(
        queryset=Pazaryeri.objects.all(),
        required=True
    )
    kategori_1 = serializers.PrimaryKeyRelatedField(
        queryset=HesaplamaKategoriler.objects.all(),
        required=True
    )

    def to_representation(self, instance):
        """
        Serializer'ın representation'ını döndürür.
        """
        # Boş instance durumunda sadece pazar yerlerini döndür
        if not instance:
            pazar_yerleri = Pazaryeri.objects.all()
            return {
                'pazar_yerleri': [
                    {
                        'id': pazar_yeri.id,
                        'pazar_ismi': pazar_yeri.pazar_ismi
                    }
                    for pazar_yeri in pazar_yerleri
                ]
            }

        data = super().to_representation(instance)
        
        # Context'ten pazar yeri ID'sini al
        pazar_yeri_id = self.context.get('pazar_yeri_id')
        if pazar_yeri_id:
            try:
                pazar_yeri = Pazaryeri.objects.get(id=pazar_yeri_id)
                data['pazar_yeri'] = pazar_yeri.id
                
                # Seviye 1 kategorileri getir (sadece seçilen pazar yerine ait)
                kategori_1_list = HesaplamaKategoriler.objects.filter(
                    pazar_yeri=pazar_yeri,
                    seviye=1
                ).order_by('adi')
                
                data['kategori_1_list'] = [
                    {
                        'id': kategori.id,
                        'adi': kategori.adi
                    }
                    for kategori in kategori_1_list
                ]
                
            except Pazaryeri.DoesNotExist:
                pass
        
        return data

class TurkishDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            # Replace comma with period for decimal numbers
            data = data.replace(',', '.')
        try:
            return super().to_internal_value(data)
        except (ValueError, InvalidOperation):
            raise serializers.ValidationError('Geçerli bir sayı giriniz.')

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

class EksikHesaplamaSerializer(serializers.Serializer):
    """
    Eksik hesaplama formu için serializer
    """
    urun_ismi = serializers.CharField(
        label='Ürün İsmi',
        help_text='Hesaplama yapılacak ürünün ismi'
    )
    kdv_orani = serializers.FloatField(
        label='KDV Oranı',
        help_text='Ürünün KDV oranı (%)'
    )
    urun_maliyeti = serializers.FloatField(
        label='Ürün Maliyeti',
        help_text='Ürünün maliyeti (TL)'
    )
    urun_paketleme_maliyeti = serializers.FloatField(
        label='Ürün Paketleme Maliyeti',
        help_text='Ürünün paketleme maliyeti (TL)'
    )
    desi_kg = serializers.FloatField(
        label='Desi/Kg',
        help_text='Ürünün desi veya kg değeri'
    )
    kargo_firma = serializers.ChoiceField(
        choices=[],
        label='Kargo Firması',
        help_text='Kargo firması seçiniz',
        style={'base_template': 'select.html', 'template_pack': 'rest_framework/vertical'}
    )
    istenilen_kar_orani = serializers.FloatField(
        label='İstenilen Kar Oranı',
        help_text='İstenilen kar oranı (%)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Kargo firma seçeneklerini dinamik olarak al
        kargo_firmalar = KargoFirma.objects.all()
        self.fields['kargo_firma'].choices = [(firma.firma_ismi, firma.firma_ismi) for firma in kargo_firmalar] 

class KargoUcretEklemeSerializer(serializers.Serializer):
    """
    Kargo ücreti ekleme için serializer
    """
    pazar_yeri = serializers.PrimaryKeyRelatedField(
        queryset=Pazaryeri.objects.filter(aktif=True),
        required=True,
        help_text="Pazar yeri seçiniz"
    )
    excel_dosya = serializers.FileField(
        required=True,
        help_text="Excel dosyasını yükleyiniz"
    ) 

class KomisyonEklemeSerializer(serializers.Serializer):
    """
    Komisyon oranı ekleme için serializer
    """
    pazar_yeri = serializers.PrimaryKeyRelatedField(
        queryset=Pazaryeri.objects.filter(aktif=True),
        required=True,
        help_text="Pazar yeri seçiniz"
    )
    kategori_seviyesi = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=4,
        help_text="Kategori seviyesi (1-4 arası)"
    )
    excel_dosya = serializers.FileField(
        required=True,
        help_text="Excel dosyasını yükleyiniz"
    ) 

class HesaplamaKategorilerSerializer(serializers.ModelSerializer):
    """
    HesaplamaKategoriler modeli için serializer
    """
    ust_kategori_adi = serializers.SerializerMethodField()
    
    class Meta:
        model = HesaplamaKategoriler
        fields = ['id', 'adi', 'ust_kategori', 'ust_kategori_adi', 'seviye', 'pazar_yeri']
    
    def get_ust_kategori_adi(self, obj):
        if obj.ust_kategori:
            return obj.ust_kategori.adi
        return None

class HesaplamaKomisyonOranlariSerializer(serializers.ModelSerializer):
    """
    HesaplamaKomisyonOranlari modeli için serializer
    """
    kategori_yolu = serializers.SerializerMethodField()
    
    class Meta:
        model = HesaplamaKomisyonOranlari
        fields = ['id', 'pazar_yeri', 'kategori_1', 'kategori_2', 'kategori_3', 'kategori_4', 
                 'komisyon_orani', 'gecerlilik_tarihi', 'kategori_yolu']
    
    def get_kategori_yolu(self, obj):
        yol = obj.kategori_1.adi
        if obj.kategori_2:
            yol += f" > {obj.kategori_2.adi}"
        if obj.kategori_3:
            yol += f" > {obj.kategori_3.adi}"
        if obj.kategori_4:
            yol += f" > {obj.kategori_4.adi}"
        return yol

class YeniKategoriKomisyonBulmaSerializer(serializers.Serializer):
    """
    Yeni yapıya uygun kategori komisyon bulma serializer'ı
    """
    email = serializers.EmailField(
        help_text="E-posta adresi",
        required=False
    )
    pazar_yeri = serializers.PrimaryKeyRelatedField(
        queryset=Pazaryeri.objects.filter(aktif=True),
        help_text="Pazar yeri seçiniz",
        required=True
    )
    kategori_1 = serializers.PrimaryKeyRelatedField(
        queryset=HesaplamaKategoriler.objects.filter(seviye=1),
        help_text="Kategori seçiniz",
        required=True
    )
    kategori_2 = serializers.PrimaryKeyRelatedField(
        queryset=HesaplamaKategoriler.objects.filter(seviye=2),
        help_text="Alt kategori seçiniz",
        required=False
    )
    kategori_3 = serializers.PrimaryKeyRelatedField(
        queryset=HesaplamaKategoriler.objects.filter(seviye=3),
        help_text="Alt kategori seçiniz",
        required=False
    )
    kategori_4 = serializers.PrimaryKeyRelatedField(
        queryset=HesaplamaKategoriler.objects.filter(seviye=4),
        help_text="Alt kategori seçiniz",
        required=False
    )
    
    def to_representation(self, instance):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        # Aktif pazar yerlerini al
        pazar_yerleri = Pazaryeri.objects.filter(aktif=True)
        pazar_yeri_choices = [
            {'id': pazar_yeri.id, 'pazar_ismi': pazar_yeri.pazar_ismi}
            for pazar_yeri in pazar_yerleri
        ]
        
        # Eğer pazar yeri seçilmişse, o pazar yerine ait kategorileri al
        pazar_yeri_id = self.context.get('pazar_yeri_id')
        if pazar_yeri_id:
            # Seviye 1 kategorileri
            kategori_1_choices = HesaplamaKategoriler.objects.filter(
                pazar_yeri_id=pazar_yeri_id,
                seviye=1
            ).order_by('adi')
            kategori_1_data = [
                {'id': kategori.id, 'adi': kategori.adi}
                for kategori in kategori_1_choices
            ]
            
            # Seviye 2 kategorileri (eğer kategori_1 seçilmişse)
            kategori_1_id = self.context.get('kategori_1_id')
            kategori_2_data = []
            if kategori_1_id:
                kategori_2_choices = HesaplamaKategoriler.objects.filter(
                    pazar_yeri_id=pazar_yeri_id,
                    seviye=2,
                    ust_kategori_id=kategori_1_id
                ).order_by('adi')
                kategori_2_data = [
                    {'id': kategori.id, 'adi': kategori.adi}
                    for kategori in kategori_2_choices
                ]
            
            # Seviye 3 kategorileri (eğer kategori_2 seçilmişse)
            kategori_2_id = self.context.get('kategori_2_id')
            kategori_3_data = []
            if kategori_2_id:
                kategori_3_choices = HesaplamaKategoriler.objects.filter(
                    pazar_yeri_id=pazar_yeri_id,
                    seviye=3,
                    ust_kategori_id=kategori_2_id
                ).order_by('adi')
                kategori_3_data = [
                    {'id': kategori.id, 'adi': kategori.adi}
                    for kategori in kategori_3_choices
                ]
            
            # Seviye 4 kategorileri (eğer kategori_3 seçilmişse)
            kategori_3_id = self.context.get('kategori_3_id')
            kategori_4_data = []
            if kategori_3_id:
                kategori_4_choices = HesaplamaKategoriler.objects.filter(
                    pazar_yeri_id=pazar_yeri_id,
                    seviye=4,
                    ust_kategori_id=kategori_3_id
                ).order_by('adi')
                kategori_4_data = [
                    {'id': kategori.id, 'adi': kategori.adi}
                    for kategori in kategori_4_choices
                ]
            
            return {
                'pazar_yeri_choices': pazar_yeri_choices,
                'kategori_1_choices': kategori_1_data,
                'kategori_2_choices': kategori_2_data,
                'kategori_3_choices': kategori_3_data,
                'kategori_4_choices': kategori_4_data
            }
        
        return {
            'pazar_yeri_choices': pazar_yeri_choices
        } 

class KomisyonOraniBulmaSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        help_text="Misafir kullanıcılar için email adresi"
    )
    pazar_yeri = serializers.PrimaryKeyRelatedField(
        queryset=Pazaryeri.objects.filter(aktif=True),
        required=True,
        help_text="Pazar yeri seçiniz"
    )
    kategori_yolu = serializers.PrimaryKeyRelatedField(
        queryset=HesaplamaKomisyonOranlari.objects.all(),
        required=True,
        help_text="Kategori yolu seçiniz",
        label="Kategori Ağacı"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Eğer pazar_yeri_id verilmişse, kategori_yolu queryset'ini filtreleme
        pazar_yeri_id = kwargs.get('context', {}).get('pazar_yeri_id')
        if pazar_yeri_id:
            self.fields['kategori_yolu'].queryset = HesaplamaKomisyonOranlari.objects.filter(
                pazar_yeri_id=pazar_yeri_id
            )
        else:
            # Başlangıçta hiçbir kategori yolu seçilemesin
            self.fields['kategori_yolu'].queryset = HesaplamaKomisyonOranlari.objects.none()

    def to_representation(self, instance):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        # Aktif pazar yerlerini al
        pazar_yerleri = Pazaryeri.objects.filter(aktif=True)
        pazar_yeri_choices = [
            {'id': None, 'pazar_ismi': '---- Pazar Yeri Seçiniz ----'}
        ] + [
            {'id': pazar_yeri.id, 'pazar_ismi': pazar_yeri.pazar_ismi}
            for pazar_yeri in pazar_yerleri
        ]
        
        # Response data hazırla
        data = {
            'pazar_yeri_choices': pazar_yeri_choices,
            'kategori_yolu_choices': [{'id': None, 'kategori_yolu': '---- Kategori Ağacı Seçiniz ----'}]
        }
        
        # Eğer pazar yeri seçilmişse, o pazar yerine ait kategori yollarını al
        pazar_yeri_id = self.context.get('pazar_yeri_id')
        if pazar_yeri_id:
            kategori_yollari = HesaplamaKomisyonOranlari.objects.filter(
                pazar_yeri_id=pazar_yeri_id
            ).select_related(
                'kategori_1',
                'kategori_2',
                'kategori_3',
                'kategori_4'
            ).order_by('kategori_1__adi')
            
            kategori_yolu_choices = [
                {'id': None, 'kategori_yolu': '---- Kategori Ağacı Seçiniz ----'}
            ]
            
            for ko in kategori_yollari:
                yol = ko.kategori_1.adi
                if ko.kategori_2:
                    yol += f" > {ko.kategori_2.adi}"
                if ko.kategori_3:
                    yol += f" > {ko.kategori_3.adi}"
                if ko.kategori_4:
                    yol += f" > {ko.kategori_4.adi}"
                
                kategori_yolu_choices.append({
                    'id': ko.id,
                    'kategori_yolu': yol,
                    'komisyon_orani': ko.komisyon_orani
                })
            
            data['kategori_yolu_choices'] = kategori_yolu_choices
        
        return data 

class FiyatHesaplamaSerializer(serializers.Serializer):
    """
    Fiyat hesaplama için serializer
    """
    email = serializers.EmailField(required=False, allow_blank=True)
    pazar_yeri = serializers.PrimaryKeyRelatedField(queryset=Pazaryeri.objects.all())
    urun_maliyeti = serializers.DecimalField(max_digits=10, decimal_places=2)
    paketleme_bedeli = serializers.DecimalField(max_digits=10, decimal_places=2)
    urun_desi_kg = serializers.DecimalField(max_digits=10, decimal_places=2)
    kargo_firma = serializers.PrimaryKeyRelatedField(queryset=KargoFirma.objects.all())
    kategori_yolu = serializers.PrimaryKeyRelatedField(queryset=HesaplamaKategoriler.objects.all())
    kar_orani = serializers.DecimalField(max_digits=5, decimal_places=2)
    kdv_orani = serializers.DecimalField(max_digits=5, decimal_places=2)

    def to_representation(self, instance):
        """
        GET isteği için form verilerini ve seçenekleri döndürür
        """
        if not instance:
            return {
                'pazar_yerleri': [
                    {'id': p.id, 'pazar_ismi': p.pazar_ismi}
                    for p in Pazaryeri.objects.all()
                ],
                'kargo_firmalari': [
                    {'id': k.id, 'firma_ismi': k.firma_ismi}
                    for k in KargoFirma.objects.filter(aktif=True)
                ],
                'kategoriler': [
                    {'id': k.id, 'ad': k.ad}
                    for k in HesaplamaKategoriler.objects.all()
                ]
            }
        return super().to_representation(instance) 

class DesiKgHesaplamaSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    en = serializers.FloatField(min_value=0)
    boy = serializers.FloatField(min_value=0)
    yukseklik = serializers.FloatField(min_value=0)
    net_agirlik = serializers.FloatField(min_value=0, required=False, default=0)

    def to_representation(self, instance):
        return {
            'email': '',
            'en': 0,
            'boy': 0,
            'yukseklik': 0,
            'net_agirlik': 0
        }

class MarketplacePriceCalculationSerializer(serializers.Serializer):
    """
    Pazar yeri satış fiyatı hesaplama için serializer
    """
    email = serializers.EmailField(required=False)
    pazar_yeri = serializers.PrimaryKeyRelatedField(queryset=Pazaryeri.objects.filter(aktif=True))
    urun_maliyeti = serializers.DecimalField(max_digits=10, decimal_places=2)
    paketleme_bedeli = serializers.DecimalField(max_digits=10, decimal_places=2)
    urun_desi_kg = serializers.DecimalField(max_digits=10, decimal_places=2)
    kargo_firma = serializers.PrimaryKeyRelatedField(queryset=KargoFirma.objects.filter(aktif=True))
    komisyon_orani = serializers.DecimalField(max_digits=5, decimal_places=2)
    kar_orani = serializers.DecimalField(max_digits=5, decimal_places=2)
    kdv_orani = serializers.DecimalField(max_digits=5, decimal_places=2)

    def to_representation(self, instance):
        """
        Form verilerini ve seçenekleri döndürür
        """
        data = {
            'pazar_yerleri': [
                {'id': pazar_yeri.id, 'pazar_ismi': pazar_yeri.pazar_ismi}
                for pazar_yeri in Pazaryeri.objects.filter(aktif=True)
            ],
            'kargo_firmalari': [
                {'id': kargo_firma.id, 'firma_ismi': kargo_firma.firma_ismi}
                for kargo_firma in KargoFirma.objects.filter(aktif=True)
            ]
        }
        return data 