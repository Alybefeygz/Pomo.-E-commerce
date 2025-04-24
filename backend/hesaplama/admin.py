from django.contrib import admin
from .models import (
    Pazaryeri, KargoFirma, DesiKgDeger, DesiKgKargoUcret, PazaryeriKargofirma,
    Kategori, AltKategori, UrunGrubu, KomisyonOrani,
    Hesaplamalar, KargoHesaplamaGecmisi, HesaplamaKategoriSeviyeleri,
    HesaplamaKategoriler, HesaplamaKomisyonOranlari,
    KategoriYolu
)

# Register your models here.
@admin.register(Pazaryeri)
class PazaryeriAdmin(admin.ModelAdmin):
    list_display = ('id', 'pazar_ismi', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('pazar_ismi',)
    list_display_links = ('id', 'pazar_ismi')

@admin.register(KargoFirma)
class KargoFirmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'firma_ismi', 'logo', 'aktif')
    list_filter = ('aktif',)
    search_fields = ('firma_ismi',)
    list_display_links = ('id', 'firma_ismi')
    fields = ('firma_ismi', 'logo', 'aktif')

@admin.register(DesiKgDeger)
class DesiKgDegerAdmin(admin.ModelAdmin):
    list_display = ('id', 'pazar_yeri', 'desi_degeri')
    list_filter = ('pazar_yeri',)
    search_fields = ('desi_degeri', 'pazar_yeri__pazar_ismi')

@admin.register(DesiKgKargoUcret)
class DesiKgKargoUcretAdmin(admin.ModelAdmin):
    list_display = ('id', 'pazar_yeri', 'kargo_firma', 'desi_kg_deger', 'ucret')
    list_filter = ('pazar_yeri', 'kargo_firma', 'desi_kg_deger')
    search_fields = ('pazar_yeri__pazar_ismi', 'kargo_firma__firma_ismi', 'desi_kg_deger__desi_degeri')

@admin.register(PazaryeriKargofirma)
class PazaryeriKargofirmaAdmin(admin.ModelAdmin):
    list_display = ('id', 'pazar_yeri', 'kargo_firma')
    list_filter = ('pazar_yeri', 'kargo_firma')
    search_fields = ('pazar_yeri__pazar_ismi', 'kargo_firma__firma_ismi')

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

@admin.register(KargoHesaplamaGecmisi)
class KargoHesaplamaGecmisiAdmin(admin.ModelAdmin):
    list_display = ('id', 'kullanici', 'email', 'olusturma_tarihi')
    list_filter = ('olusturma_tarihi',)
    search_fields = ('kullanici__username', 'email')

@admin.register(HesaplamaKategoriSeviyeleri)
class HesaplamaKategoriSeviyeleriAdmin(admin.ModelAdmin):
    list_display = ('pazar_yeri', 'maksimum_seviye')
    list_filter = ('maksimum_seviye',)
    search_fields = ('pazar_yeri__pazar_ismi',)

@admin.register(HesaplamaKategoriler)
class HesaplamaKategorilerAdmin(admin.ModelAdmin):
    list_display = ('adi', 'ust_kategori', 'seviye')
    list_filter = ('seviye',)
    search_fields = ('adi', 'ust_kategori__adi')
    ordering = ('seviye', 'adi')

@admin.register(HesaplamaKomisyonOranlari)
class HesaplamaKomisyonOranlariAdmin(admin.ModelAdmin):
    list_display = ('pazar_yeri', 'kategori_1', 'kategori_2', 'kategori_3', 'kategori_4', 'komisyon_orani', 'gecerlilik_tarihi')
    list_filter = ('pazar_yeri', 'gecerlilik_tarihi')
    search_fields = ('pazar_yeri__pazar_ismi', 'kategori_1__adi', 'kategori_2__adi', 'kategori_3__adi', 'kategori_4__adi')
    ordering = ('pazar_yeri', 'kategori_1', 'kategori_2', 'kategori_3', 'kategori_4')

@admin.register(KategoriYolu)
class KategoriYoluAdmin(admin.ModelAdmin):
    """
    KategoriYolu modeli için admin panel ayarları.
    """
    list_display = ('pazar_yeri', 'ad', 'komisyon_orani', 'ust_kategori')
    list_filter = ('pazar_yeri',)
    search_fields = ('ad', 'pazar_yeri__pazar_ismi')
    raw_id_fields = ('ust_kategori',)
    autocomplete_fields = ('pazar_yeri',)
