from django.contrib import admin
from .models import (
    KargoFirma, DesiKgDeger, DesiKgKargoUcret, 
    Kategori, AltKategori, UrunGrubu, KomisyonOrani,
    Hesaplamalar, FiyatBelirleme
)

# Register your models here.
@admin.register(KargoFirma)
class KargoFirmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'firma_ismi', 'logo')
    search_fields = ('firma_ismi',)
    list_display_links = ('id', 'firma_ismi')
    fields = ('firma_ismi', 'logo')

@admin.register(DesiKgDeger)
class DesiKgDegerAdmin(admin.ModelAdmin):
    list_display = ('id', 'desi_degeri')
    search_fields = ('desi_degeri',)

@admin.register(DesiKgKargoUcret)
class DesiKgKargoUcretAdmin(admin.ModelAdmin):
    list_display = ('id', 'kargo_firma', 'desi_kg_deger', 'fiyat')
    list_filter = ('kargo_firma', 'desi_kg_deger')
    search_fields = ('kargo_firma__firma_ismi',)

# Trendyol Kategori Komisyon Oranları için Admin Sınıfları
@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ('id', 'kategori_adi')
    search_fields = ('kategori_adi',)

@admin.register(AltKategori)
class AltKategoriAdmin(admin.ModelAdmin):
    list_display = ('id', 'kategori', 'alt_kategori_adi')
    list_filter = ('kategori',)
    search_fields = ('alt_kategori_adi', 'kategori__kategori_adi')

@admin.register(UrunGrubu)
class UrunGrubuAdmin(admin.ModelAdmin):
    list_display = ('id', 'alt_kategori', 'urun_grubu_adi')
    list_filter = ('alt_kategori__kategori', 'alt_kategori')
    search_fields = ('urun_grubu_adi', 'alt_kategori__alt_kategori_adi')

@admin.register(KomisyonOrani)
class KomisyonOraniAdmin(admin.ModelAdmin):
    list_display = ('id', 'urun_grubu', 'komisyon_orani')
    list_filter = ('urun_grubu__alt_kategori__kategori', 'urun_grubu__alt_kategori')
    search_fields = ('urun_grubu__urun_grubu_adi',)

# Yeni eklenen modeller için Admin sınıfları
@admin.register(Hesaplamalar)
class HesaplamalarAdmin(admin.ModelAdmin):
    list_display = ('hesaplama_id', 'kullanici', 'email', 'olusturulma_tarihi', 'toplam_fiyat')
    list_filter = ('kullanici', 'olusturulma_tarihi')
    search_fields = ('kullanici__username', 'email')
    date_hierarchy = 'olusturulma_tarihi'

@admin.register(FiyatBelirleme)
class FiyatBelirlemeAdmin(admin.ModelAdmin):
    list_display = ('urun_id', 'urun_ismi', 'hesaplama', 'urun_maliyeti', 'satis_fiyati_kdv_dahil')
    list_filter = ('hesaplama__kullanici', 'urun_kategorisi')
    search_fields = ('urun_ismi', 'urun_kategorisi', 'hesaplama__kullanici__username', 'hesaplama__email')
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('hesaplama', 'urun_ismi', 'urun_maliyeti', 'paketleme_maliyeti')
        }),
        ('Kargo Bilgileri', {
            'fields': ('kargo_firmasi', 'kargo_ucreti', 'desi_kg_degeri')
        }),
        ('Komisyon ve Fiyatlandırma', {
            'fields': ('urun_kategorisi', 'komisyon_orani', 'komisyon_tutari', 
                       'trendyol_hizmet_bedeli', 'stopaj_degeri')
        }),
        ('Satış Bilgileri', {
            'fields': ('kdv_orani', 'kar_orani', 'kar_tutari', 
                       'satis_fiyati_kdv_haric', 'satis_fiyati_kdv_dahil')
        }),
    )
