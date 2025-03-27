from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class KargoFirma(models.Model):
    firma_ismi = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='kargo_logo/', null=True, blank=True)

    def __str__(self):
        return self.firma_ismi

class DesiKgDeger(models.Model):
    desi_degeri = models.FloatField()

    def __str__(self):
        return str(self.desi_degeri)

class DesiKgKargoUcret(models.Model):
    kargo_firma = models.ForeignKey(KargoFirma, on_delete=models.CASCADE, related_name='kargo_ucretleri')
    desi_kg_deger = models.ForeignKey(DesiKgDeger, on_delete=models.CASCADE, related_name='kargo_ucretleri')
    fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.kargo_firma} - {self.desi_kg_deger} - {self.fiyat} TL"

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
