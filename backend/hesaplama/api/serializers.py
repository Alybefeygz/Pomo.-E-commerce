from rest_framework import serializers
from hesaplama.models import KargoFirma, DesiKgDeger, DesiKgKargoUcret, Kategori, AltKategori, UrunGrubu, KomisyonOrani
from decimal import Decimal, InvalidOperation
from django.contrib.auth import get_user_model

class KargoFirmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = KargoFirma
        fields = ['id', 'firma_ismi', 'logo']

class DesiKgDegerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesiKgDeger
        fields = ['id', 'desi_degeri']

class DesiKgKargoUcretSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesiKgKargoUcret
        fields = ['id', 'kargo_firma', 'desi_kg_deger', 'fiyat']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['kargo_firma'] = instance.kargo_firma.firma_ismi
        representation['desi_kg_deger'] = instance.desi_kg_deger.desi_degeri
        return representation

class KargoUcretHesaplamaSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="E-posta adresi"
    )
    en = serializers.FloatField(
        min_value=0.01,
        help_text="Kargonun eni (cm)"
    )
    boy = serializers.FloatField(
        min_value=0.01,
        help_text="Kargonun boyu (cm)"
    )
    yukseklik = serializers.FloatField(
        min_value=0.01,
        help_text="Kargonun yüksekliği (cm)"
    )
    net_agirlik = serializers.FloatField(
        min_value=0.01,
        help_text="Kargonun net ağırlığı (kg)"
    )
    kargo_firma = serializers.ChoiceField(
        choices=[],
        help_text="Kargo firması seçiniz"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Kargo firma seçeneklerini dinamik olarak belirle
        context = kwargs.get('context', {})
        kargo_firma_secenekleri = context.get('kargo_firma_secenekleri', {})
        
        if not kargo_firma_secenekleri:
            # Context'te firma bilgisi yoksa, veritabanından çek
            kargo_firmalar = KargoFirma.objects.all()
            kargo_firma_secenekleri = {str(firma.id): firma.firma_ismi for firma in kargo_firmalar}
        
        self.fields['kargo_firma'].choices = [(k, v) for k, v in kargo_firma_secenekleri.items()]

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
    urun_grubu = UrunGrubuSerializer(read_only=True)
    urun_grubu_id = serializers.PrimaryKeyRelatedField(
        queryset=UrunGrubu.objects.all(), 
        source='urun_grubu',
        write_only=True
    )
    
    class Meta:
        model = KomisyonOrani
        fields = ['id', 'urun_grubu', 'urun_grubu_id', 'komisyon_orani']
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['komisyon_orani'] = f"{instance.komisyon_orani}"
        return representation 

class KategoriKomisyonBulmaSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="E-posta adresi"
    )
    kategori = serializers.PrimaryKeyRelatedField(
        queryset=Kategori.objects.all(),
        help_text="Kategori seçiniz",
        required=False
    )
    alt_kategori = serializers.PrimaryKeyRelatedField(
        queryset=AltKategori.objects.all(),
        help_text="Alt kategori seçiniz",
        required=False
    )
    urun_grubu = serializers.PrimaryKeyRelatedField(
        queryset=UrunGrubu.objects.all(),
        help_text="Ürün grubu seçiniz",
        required=False
    )
    
    def to_representation(self, instance):
        # Eğer bu bir POST response ise ve instance bir KomisyonOrani ise
        if isinstance(instance, KomisyonOrani):
            return {
                'email': self.context.get('email', ''),  # Email'i context'ten al
                'id': instance.id,
                'kategori': {
                    'id': instance.urun_grubu.alt_kategori.kategori.id,
                    'kategori_adi': instance.urun_grubu.alt_kategori.kategori.kategori_adi
                },
                'alt_kategori': {
                    'id': instance.urun_grubu.alt_kategori.id,
                    'alt_kategori_adi': instance.urun_grubu.alt_kategori.alt_kategori_adi
                },
                'urun_grubu': {
                    'id': instance.urun_grubu.id,
                    'urun_grubu_adi': instance.urun_grubu.urun_grubu_adi
                },
                'komisyon_orani': f"{instance.komisyon_orani}"
            }
        # Eğer bu bir GET request için boş form ise
        return super().to_representation(instance) 

class TurkishDecimalField(serializers.DecimalField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            # Replace comma with period for decimal numbers
            data = data.replace(',', '.')
        try:
            return super().to_internal_value(data)
        except (ValueError, InvalidOperation):
            raise serializers.ValidationError('Geçerli bir sayı giriniz.')

class SatisFiyatBelirlemeSerializer(serializers.Serializer):
    email = serializers.EmailField(
        help_text="E-posta adresi"
    )
    urun_ismi = serializers.CharField(
        max_length=255,
        help_text="Ürün ismi"
    )
    kdv_orani = TurkishDecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="KDV oranı (%)",
        min_value=0,
        max_value=100
    )
    urun_maliyeti = TurkishDecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Ürün maliyeti"
    )
    urun_paketleme_maliyeti = TurkishDecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Ürün paketleme maliyeti"
    )
    en = serializers.FloatField(
        min_value=0.01,
        help_text="Ürünün eni (cm)"
    )
    boy = serializers.FloatField(
        min_value=0.01,
        help_text="Ürünün boyu (cm)"
    )
    yukseklik = serializers.FloatField(
        min_value=0.01,
        help_text="Ürünün yüksekliği (cm)"
    )
    net_agirlik = serializers.FloatField(
        min_value=0.01,
        help_text="Ürünün net ağırlığı (kg)"
    )
    kargo_firma = serializers.ChoiceField(
        choices=[],
        help_text="Kargo firması seçiniz"
    )
    kategori = serializers.PrimaryKeyRelatedField(
        queryset=Kategori.objects.all(),
        help_text="Kategori seçiniz",
        required=False
    )
    alt_kategori = serializers.PrimaryKeyRelatedField(
        queryset=AltKategori.objects.all(),
        help_text="Alt kategori seçiniz",
        required=False
    )
    urun_grubu = serializers.PrimaryKeyRelatedField(
        queryset=UrunGrubu.objects.all(),
        help_text="Ürün grubu seçiniz",
        required=False
    )
    istenilen_kar_orani = TurkishDecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="İstenilen kâr oranı (%)",
        min_value=0
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Kargo firmaları seçeneklerini al
        context = kwargs.get('context', {})
        kargo_firma_secenekleri = context.get('kargo_firma_secenekleri', {})
        
        # ChoiceField'in choices parametresini güncelle
        choices = []
        if kargo_firma_secenekleri:
            for k, v in kargo_firma_secenekleri.items():
                choices.append((str(k), str(v)))  # String olarak ID'leri kullan
        
        self.fields['kargo_firma'].choices = choices
        
    def validate_kargo_firma(self, value):
        """
        Kargo firma alanını doğrula.
        Boş değer veya geçersiz seçim durumunda hata ver.
        """
        if not value or value == "":
            raise serializers.ValidationError("Lütfen bir kargo firması seçiniz.")
        return value

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