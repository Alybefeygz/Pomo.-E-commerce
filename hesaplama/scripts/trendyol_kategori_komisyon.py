import os
import sys
import pandas as pd
import django
from decimal import Decimal, InvalidOperation

# Add the backend directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hesaplama.models import Kategori, AltKategori, UrunGrubu, KomisyonOrani

def import_trendyol_kategori_komisyon_data():
    """
    Trendyol Kategori Komisyon Oranları Excel dosyasından verileri okuyup veritabanına aktaran fonksiyon.
    
    Bu fonksiyon şunları yapar:
    1. Excel dosyasını okur
    2. Kategori, Alt Kategori, Ürün Grubu ve Komisyon Oranı modellerini oluşturur
    3. Excel'deki verileri bu modellere aktarır
    """
    try:
        # Excel dosyasının yolu (projenin kök dizinindeki Excel dosyası)
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
            "Trendyol Kategori Komisyon Oranları (Temizlenmiş Hali).xlsx"
        )
        
        print(f"Excel dosyası yolu: {file_path}")
        
        # Excel dosyasını pandas ile oku
        df = pd.read_excel(file_path)
        
        # Excel verilerindeki sütun adlarını kontrol et
        print(f"Excel sütun adları: {df.columns.tolist()}")
        
        # Veri yapısını kontrol etmek için birkaç satır göster
        print("İlk 5 satır:")
        print(df.head())
        
        # Sütun adlarını doğru şekilde belirle
        kategori_column = "Kategori"  # Kategori sütunu
        alt_kategori_column = "Alt Kategori"  # Alt Kategori sütunu
        urun_grubu_column = "Ürün Grubu"  # Ürün Grubu sütunu
        komisyon_column = "Kategori Komisyon % (KDV Dahil)"  # Komisyon Oranı sütunu
        
        print(f"Kategori Sütunu: {kategori_column}")
        print(f"Alt Kategori Sütunu: {alt_kategori_column}")
        print(f"Ürün Grubu Sütunu: {urun_grubu_column}")
        print(f"Komisyon Oranı Sütunu: {komisyon_column}")
        
        # Kategorileri oluştur (benzersiz kategoriler)
        unique_kategoriler = df[kategori_column].dropna().unique()
        print(f"Benzersiz kategori sayısı: {len(unique_kategoriler)}")
        
        kategori_objects = {}
        for kategori_adi in unique_kategoriler:
            kategori, created = Kategori.objects.get_or_create(kategori_adi=kategori_adi)
            kategori_objects[kategori_adi] = kategori
            if created:
                print(f"Kategori oluşturuldu: {kategori_adi}")
            else:
                print(f"Var olan kategori: {kategori_adi}")
        
        # Alt kategorileri oluştur
        alt_kategori_objects = {}
        for _, row in df.iterrows():
            kategori_adi = row[kategori_column]
            alt_kategori_adi = row[alt_kategori_column]
            
            # Boş değerleri atla
            if pd.isna(kategori_adi) or pd.isna(alt_kategori_adi):
                continue
            
            kategori = kategori_objects[kategori_adi]
            alt_kategori_key = f"{kategori_adi}_{alt_kategori_adi}"
            
            if alt_kategori_key not in alt_kategori_objects:
                alt_kategori, created = AltKategori.objects.get_or_create(
                    kategori=kategori,
                    alt_kategori_adi=alt_kategori_adi
                )
                alt_kategori_objects[alt_kategori_key] = alt_kategori
                
                if created:
                    print(f"Alt kategori oluşturuldu: {kategori_adi} > {alt_kategori_adi}")
                else:
                    print(f"Var olan alt kategori: {kategori_adi} > {alt_kategori_adi}")
        
        # Ürün gruplarını ve komisyon oranlarını oluştur
        urun_grubu_objects = {}
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for idx, row in df.iterrows():
            try:
                kategori_adi = row[kategori_column]
                alt_kategori_adi = row[alt_kategori_column]
                urun_grubu_adi = row[urun_grubu_column]
                komisyon_orani_value = row[komisyon_column]
                
                # Boş değerleri atla
                if pd.isna(kategori_adi) or pd.isna(alt_kategori_adi) or pd.isna(urun_grubu_adi) or pd.isna(komisyon_orani_value):
                    print(f"Satır {idx}: Boş değer bulundu, atlıyorum.")
                    continue
                
                # Alt kategoriyi bul
                alt_kategori_key = f"{kategori_adi}_{alt_kategori_adi}"
                if alt_kategori_key not in alt_kategori_objects:
                    print(f"Satır {idx}: Hata: Alt kategori bulunamadı: {alt_kategori_key}")
                    continue
                    
                alt_kategori = alt_kategori_objects[alt_kategori_key]
                
                # Ürün grubunu oluştur veya bul
                urun_grubu_key = f"{alt_kategori_key}_{urun_grubu_adi}"
                
                if urun_grubu_key not in urun_grubu_objects:
                    urun_grubu, created = UrunGrubu.objects.get_or_create(
                        alt_kategori=alt_kategori,
                        urun_grubu_adi=urun_grubu_adi
                    )
                    urun_grubu_objects[urun_grubu_key] = urun_grubu
                    
                    if created:
                        print(f"Ürün grubu oluşturuldu: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi}")
                    else:
                        print(f"Var olan ürün grubu: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi}")
                else:
                    urun_grubu = urun_grubu_objects[urun_grubu_key]
                
                # Komisyon oranını düzenle
                try:
                    # Veri hakkında bilgi
                    print(f"Satır {idx}: Komisyon oranı: {komisyon_orani_value}, Tür: {type(komisyon_orani_value)}")
                    
                    # Eğer veri zaten float ise doğrudan kullan
                    if isinstance(komisyon_orani_value, (float, int)):
                        komisyon_orani_decimal = Decimal(str(komisyon_orani_value))
                    # Eğer string ise temizle ve dönüştür
                    elif isinstance(komisyon_orani_value, str):
                        # Yüzde işareti, virgül ve diğer karakterleri temizle
                        cleaned_value = komisyon_orani_value.replace('%', '').replace(',', '.').strip()
                        komisyon_orani_decimal = Decimal(cleaned_value)
                    else:
                        print(f"Satır {idx}: Hata: Desteklenmeyen veri tipi - {type(komisyon_orani_value)}")
                        error_count += 1
                        continue
                    
                    # Eğer 0-1 arasında bir değerse (örn: 0.15), yüzde formatına çevir (15)
                    if komisyon_orani_decimal < 1:
                        komisyon_orani_decimal = komisyon_orani_decimal * 100
                    
                    # Komisyon oranını oluştur veya güncelle
                    komisyon, created = KomisyonOrani.objects.update_or_create(
                        urun_grubu=urun_grubu,
                        defaults={'komisyon_orani': komisyon_orani_decimal}
                    )
                    
                    if created:
                        created_count += 1
                        print(f"Komisyon oranı oluşturuldu: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi} - %{komisyon_orani_decimal}")
                    else:
                        updated_count += 1
                        print(f"Komisyon oranı güncellendi: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi} - %{komisyon_orani_decimal}")
                
                except (ValueError, TypeError, InvalidOperation) as e:
                    print(f"Satır {idx}: Hata: Komisyon oranı çevrilemedi - {komisyon_orani_value} - Tür: {type(komisyon_orani_value)} - Hata: {str(e)}")
                    
                    # Hataya neden olan değerin detaylı incelemesi
                    if isinstance(komisyon_orani_value, str):
                        print(f"  String değer: '{komisyon_orani_value}', Unicode karakterleri: {[ord(c) for c in komisyon_orani_value]}")
                    else:
                        print(f"  Değer: {repr(komisyon_orani_value)}")
                    
                    # Hata sayısı artır
                    error_count += 1
            except Exception as e:
                print(f"Satır {idx}: İşleme hatası: {str(e)}")
                error_count += 1
        
        print(f"Toplam {created_count} yeni komisyon oranı kaydı oluşturuldu.")
        print(f"Toplam {updated_count} var olan komisyon oranı kaydı güncellendi.")
        print(f"Toplam {error_count} komisyon oranı kaydı oluşturulamadı.")
        print("İşlem başarılı bir şekilde tamamlandı.")
        
        return True, "Veri içe aktarımı başarıyla tamamlandı."
        
    except Exception as e:
        import traceback
        print(f"Hata oluştu: {str(e)}")
        print(traceback.format_exc())
        return False, f"Hata: {str(e)}"

if __name__ == "__main__":
    success, message = import_trendyol_kategori_komisyon_data()
    print(message)
