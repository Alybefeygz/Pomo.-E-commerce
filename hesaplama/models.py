from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal

# Create your models here.
class Pazaryeri(models.Model):
    pazar_ismi = models.CharField(max_length=100)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.pazar_ismi

    class Meta:
        verbose_name = "Pazar Yeri"
        verbose_name_plural = "Pazar Yerleri"

class KargoFirma(models.Model):
    firma_ismi = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='kargo_logo/', null=True, blank=True)
    aktif = models.BooleanField(default=True)

    def __str__(self):
        return self.firma_ismi

    class Meta:
        verbose_name = "Kargo Firması"
        verbose_name_plural = "Kargo Firmaları"

class DesiKgDeger(models.Model):
    pazar_yeri = models.ForeignKey(Pazaryeri, on_delete=models.CASCADE, related_name='desi_kg_degerleri', default=1)
    desi_degeri = models.FloatField()

    def __str__(self):
        return f"{self.pazar_yeri} - {self.desi_degeri}"

    class Meta:
        verbose_name = "Desi/Kg Değeri"
        verbose_name_plural = "Desi/Kg Değerleri"

class DesiKgKargoUcret(models.Model):
    pazar_yeri = models.ForeignKey(Pazaryeri, on_delete=models.CASCADE, related_name='kargo_ucretleri')
    desi_kg_deger = models.ForeignKey(DesiKgDeger, on_delete=models.CASCADE, related_name='kargo_ucretleri')
    kargo_firma = models.ForeignKey(KargoFirma, on_delete=models.CASCADE, related_name='kargo_ucretleri')
    ucret = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.pazar_yeri} - {self.kargo_firma} - {self.desi_kg_deger} - {self.ucret} TL"

    class Meta:
        verbose_name = "Desi/Kg Kargo Ücreti"
        verbose_name_plural = "Desi/Kg Kargo Ücretleri"

class PazaryeriKargofirma(models.Model):
    pazar_yeri = models.ForeignKey(Pazaryeri, on_delete=models.CASCADE, related_name='kargo_firmalari')
    kargo_firma = models.ForeignKey(KargoFirma, on_delete=models.CASCADE, related_name='pazar_yerleri')

    def __str__(self):
        return f"{self.pazar_yeri} - {self.kargo_firma}"

    class Meta:
        verbose_name = "Pazar Yeri Kargo Firması"
        verbose_name_plural = "Pazar Yeri Kargo Firmaları"

# Trendyol Kategori Komisyon Oranları için Modeller
class Kategori(models.Model):
    kategori_adi = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.kategori_adi
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"

class AltKategori(models.Model):
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, related_name='alt_kategoriler')
    alt_kategori_adi = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.kategori} > {self.alt_kategori_adi}"
    
    class Meta:
        verbose_name = "Alt Kategori"
        verbose_name_plural = "Alt Kategoriler"
        unique_together = ('kategori', 'alt_kategori_adi')

class UrunGrubu(models.Model):
    alt_kategori = models.ForeignKey(AltKategori, on_delete=models.CASCADE, related_name='urun_gruplari')
    urun_grubu_adi = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.alt_kategori} > {self.urun_grubu_adi}"
    
    class Meta:
        verbose_name = "Ürün Grubu"
        verbose_name_plural = "Ürün Grupları"
        unique_together = ('alt_kategori', 'urun_grubu_adi')

class KomisyonOrani(models.Model):
    urun_grubu = models.ForeignKey(UrunGrubu, on_delete=models.CASCADE, related_name='komisyon_oranlari')
    komisyon_orani = models.DecimalField(max_digits=5, decimal_places=2, help_text="Komisyon oranı (% olarak)")
    
    def __str__(self):
        return f"{self.urun_grubu} - %{self.komisyon_orani}"
    
    class Meta:
        verbose_name = "Komisyon Oranı"
        verbose_name_plural = "Komisyon Oranları"

# Hesaplamalar Tablosu
class Hesaplamalar(models.Model):
    hesaplama_id = models.AutoField(primary_key=True)
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hesaplamalar', null=True, blank=True)
    email = models.EmailField(help_text="Hesaplama yapan kullanıcının email adresi", default="guest@example.com")
    olusturulma_tarihi = models.DateTimeField(auto_now_add=True)
    toplam_fiyat = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        if self.kullanici:
            return f"Hesaplama #{self.hesaplama_id} - {self.kullanici.username}"
        return f"Hesaplama #{self.hesaplama_id} - {self.email}"
    
    class Meta:
        verbose_name = "Hesaplama"
        verbose_name_plural = "Hesaplamalar"

# Fiyat Belirleme Tablosu
class FiyatBelirleme(models.Model):
    urun_id = models.AutoField(primary_key=True)
    hesaplama = models.ForeignKey(Hesaplamalar, on_delete=models.CASCADE, related_name='fiyat_belirlemeler')
    urun_ismi = models.CharField(max_length=100)
    urun_maliyeti = models.DecimalField(max_digits=10, decimal_places=2)
    paketleme_maliyeti = models.DecimalField(max_digits=10, decimal_places=2)
    trendyol_hizmet_bedeli = models.DecimalField(max_digits=10, decimal_places=2)
    kargo_firmasi = models.CharField(max_length=50)
    kargo_ucreti = models.DecimalField(max_digits=10, decimal_places=2)
    stopaj_degeri = models.DecimalField(max_digits=10, decimal_places=2)
    desi_kg_degeri = models.DecimalField(max_digits=10, decimal_places=2)
    urun_kategorisi = models.TextField()
    komisyon_orani = models.DecimalField(max_digits=5, decimal_places=2)
    komisyon_tutari = models.DecimalField(max_digits=10, decimal_places=2)
    kdv_orani = models.DecimalField(max_digits=5, decimal_places=2)
    kar_orani = models.DecimalField(max_digits=5, decimal_places=2)
    kar_tutari = models.DecimalField(max_digits=10, decimal_places=2)
    satis_fiyati_kdv_haric = models.DecimalField(max_digits=10, decimal_places=2)
    satis_fiyati_kdv_dahil = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.urun_ismi} - Hesaplama #{self.hesaplama.hesaplama_id}"
    
    class Meta:
        verbose_name = "Fiyat Belirleme"
        verbose_name_plural = "Fiyat Belirlemeler"

class KargoHesaplamaGecmisi(models.Model):
    """
    Yapılan kargo ücreti hesaplamalarının geçmişini tutan tablo
    """
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kargo_hesaplamalari', null=True, blank=True)
    email = models.EmailField(help_text="Hesaplama yapan kullanıcının email adresi", default="guest@example.com")
    pazar_yeri = models.ForeignKey('Pazaryeri', on_delete=models.PROTECT)
    kargo_firma = models.ForeignKey('KargoFirma', on_delete=models.PROTECT)
    
    en = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    boy = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    yukseklik = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    net_agirlik = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    
    hesaplanan_desi = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="(en * boy * yükseklik) / 3000"
    )
    hesaplanan_desi_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="max(desi, net_agirlik)"
    )
    yuvarlanmis_desi_kg = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Yuvarlanmış desi/kg değeri"
    )
    
    kargo_ucreti = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Hesaplanan kargo ücreti"
    )
    
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)
    guncelleme_tarihi = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Kargo Hesaplama Geçmişi"
        verbose_name_plural = "Kargo Hesaplama Geçmişleri"
        ordering = ['-olusturma_tarihi']
    
    def __str__(self):
        user_str = self.kullanici.username if self.kullanici else self.email
        return f"{user_str} - {self.pazar_yeri.pazar_ismi} - {self.kargo_firma.firma_ismi} - {self.olusturma_tarihi}"

# Yeni Modeller - Pazar Yeri Kategori ve Komisyon Yapısı

class HesaplamaKategoriSeviyeleri(models.Model):
    """
    Her pazar yerinin desteklediği maksimum kategori seviyesini tutar
    """
    pazar_yeri = models.OneToOneField(
        Pazaryeri, 
        on_delete=models.CASCADE, 
        related_name='kategori_seviyesi'
    )
    maksimum_seviye = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Pazar yerinin desteklediği en derin kategori seviyesi (1-4 arası)"
    )
    
    def __str__(self):
        return f"{self.pazar_yeri.pazar_ismi} - Maksimum Seviye: {self.maksimum_seviye}"
    
    class Meta:
        verbose_name = "Hesaplama Kategori Seviyesi"
        verbose_name_plural = "Hesaplama Kategori Seviyeleri"
        db_table = "hesaplama_kategori_seviyeleri"

class HesaplamaKategoriler(models.Model):
    """
    Tüm kategorileri hiyerarşik yapıda tutar
    """
    adi = models.CharField(max_length=255, help_text="Kategori adı")
    ust_kategori = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='alt_kategoriler',
        null=True, 
        blank=True,
        help_text="Üst kategori referansı (hiyerarşi için)"
    )
    seviye = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text="Kategorinin seviyesi (1-4 arası)"
    )
    pazar_yeri = models.ForeignKey(
        Pazaryeri,
        on_delete=models.CASCADE,
        related_name='kategoriler',
        null=True,
        blank=True,
        help_text="Kategorinin ait olduğu pazar yeri"
    )
    
    def __str__(self):
        if self.ust_kategori:
            return f"{self.ust_kategori} > {self.adi}"
        return self.adi
    
    class Meta:
        verbose_name = "Hesaplama Kategori"
        verbose_name_plural = "Hesaplama Kategoriler"
        db_table = "hesaplama_kategoriler"

class HesaplamaKomisyonOranlari(models.Model):
    """
    Pazar yerlerine göre kategori bazlı komisyon oranlarını tutar
    """
    pazar_yeri = models.ForeignKey(
        Pazaryeri, 
        on_delete=models.CASCADE, 
        related_name='komisyon_oranlari'
    )
    kategori_1 = models.ForeignKey(
        HesaplamaKategoriler, 
        on_delete=models.CASCADE, 
        related_name='komisyon_oranlari_seviye1'
    )
    kategori_2 = models.ForeignKey(
        HesaplamaKategoriler, 
        on_delete=models.CASCADE, 
        related_name='komisyon_oranlari_seviye2',
        null=True, 
        blank=True
    )
    kategori_3 = models.ForeignKey(
        HesaplamaKategoriler, 
        on_delete=models.CASCADE, 
        related_name='komisyon_oranlari_seviye3',
        null=True, 
        blank=True
    )
    kategori_4 = models.ForeignKey(
        HesaplamaKategoriler, 
        on_delete=models.CASCADE, 
        related_name='komisyon_oranlari_seviye4',
        null=True, 
        blank=True
    )
    komisyon_orani = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Komisyon oranı yüzdesi"
    )
    gecerlilik_tarihi = models.DateField(
        help_text="Oranın geçerli olduğu tarih aralığı"
    )
    
    def __str__(self):
        kategori_yolu = self.kategori_1.adi
        if self.kategori_2:
            kategori_yolu += f" > {self.kategori_2.adi}"
        if self.kategori_3:
            kategori_yolu += f" > {self.kategori_3.adi}"
        if self.kategori_4:
            kategori_yolu += f" > {self.kategori_4.adi}"
        return f"{self.pazar_yeri.pazar_ismi} - {kategori_yolu} - %{self.komisyon_orani}"
    
    class Meta:
        verbose_name = "Hesaplama Komisyon Oranı"
        verbose_name_plural = "Hesaplama Komisyon Oranları"
        db_table = "hesaplama_komisyon_oranlari"

class KategoriYolu(models.Model):
    """
    Pazar yerlerine göre kategori yollarını tutar
    """
    pazar_yeri = models.ForeignKey(
        Pazaryeri, 
        on_delete=models.CASCADE, 
        related_name='kategori_yollari'
    )
    ad = models.CharField(max_length=255, help_text="Kategori yolu adı")
    komisyon_orani = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Komisyon oranı yüzdesi"
    )
    ust_kategori = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        related_name='alt_kategoriler',
        null=True, 
        blank=True,
        help_text="Üst kategori yolu referansı"
    )
    
    def __str__(self):
        return f"{self.pazar_yeri.pazar_ismi} - {self.ad}"
    
    class Meta:
        verbose_name = "Kategori Yolu"
        verbose_name_plural = "Kategori Yolları"
        db_table = "kategori_yollari"
        unique_together = ('pazar_yeri', 'ad')

class HesaplamaDesiKgGecmisi(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    urun_ismi = models.CharField(max_length=255, default="Ürün")
    en = models.FloatField()
    boy = models.FloatField()
    yukseklik = models.FloatField()
    net_agirlik = models.FloatField()
    desi_kg = models.FloatField()
    hesaplama_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Desi/Kg Hesaplama Geçmişi'
        verbose_name_plural = 'Desi/Kg Hesaplama Geçmişleri'

    def __str__(self):
        return f"{self.kullanici.username} - {self.hesaplama_tarihi}"

class KargoUcretGecmis(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    urun_ismi = models.CharField(max_length=255, default="Ürün")
    desi_kg_degeri = models.DecimalField(max_digits=10, decimal_places=2)
    yuvarlanmis_desi_kg = models.DecimalField(max_digits=10, decimal_places=2)
    pazar_yeri = models.ForeignKey(Pazaryeri, on_delete=models.CASCADE)
    kargo_firma = models.ForeignKey(KargoFirma, on_delete=models.CASCADE)
    kargo_ucreti = models.DecimalField(max_digits=10, decimal_places=2)
    hesaplama_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kargo Ücreti Geçmişi'
        verbose_name_plural = 'Kargo Ücreti Geçmişleri'
        ordering = ['-hesaplama_tarihi']

    def __str__(self):
        return f"{self.kullanici.username if self.kullanici else self.email} - {self.pazar_yeri.pazar_ismi} - {self.kargo_firma.firma_ismi} - {self.hesaplama_tarihi}"

class KomisyonOraniGecmisi(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    urun_ismi = models.CharField(max_length=255, default="Ürün")
    pazar_yeri = models.ForeignKey(Pazaryeri, on_delete=models.CASCADE)
    kategori_yolu = models.ForeignKey(HesaplamaKategoriler, on_delete=models.CASCADE)
    komisyon_orani = models.DecimalField(max_digits=5, decimal_places=2)
    hesaplama_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Komisyon Oranı Geçmişi'
        verbose_name_plural = 'Komisyon Oranı Geçmişleri'
        ordering = ['-hesaplama_tarihi']

    def __str__(self):
        return f"{self.kullanici.username if self.kullanici else self.email} - {self.pazar_yeri.pazar_ismi} - {self.kategori_yolu.adi} - {self.hesaplama_tarihi}"

class FiyatHesaplamaGecmisi(models.Model):
    kullanici = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    urun_ismi = models.CharField(max_length=255, default="Ürün")
    pazar_yeri = models.ForeignKey(Pazaryeri, on_delete=models.CASCADE)
    urun_maliyeti = models.DecimalField(max_digits=10, decimal_places=2)
    paketleme_bedeli = models.DecimalField(max_digits=10, decimal_places=2)
    hizmet_bedeli = models.DecimalField(max_digits=10, decimal_places=2)
    urun_desi_kg = models.DecimalField(max_digits=10, decimal_places=2)
    kargo_firma = models.ForeignKey(KargoFirma, on_delete=models.CASCADE)
    kargo_ucreti = models.DecimalField(max_digits=10, decimal_places=2)
    komisyon_orani = models.DecimalField(max_digits=5, decimal_places=2)
    stopaj_orani = models.DecimalField(max_digits=5, decimal_places=2)
    stopaj_bedeli = models.DecimalField(max_digits=10, decimal_places=2)
    satis_fiyati = models.DecimalField(max_digits=10, decimal_places=2)
    kdv_dahil_satis_fiyati = models.DecimalField(max_digits=10, decimal_places=2)
    hesaplama_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Fiyat Hesaplama Geçmişi'
        verbose_name_plural = 'Fiyat Hesaplama Geçmişleri'
        ordering = ['-hesaplama_tarihi']

    def __str__(self):
        return f"{self.kullanici.username if self.kullanici else self.email} - {self.pazar_yeri.pazar_ismi} - {self.hesaplama_tarihi}"
