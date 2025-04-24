import os
import sys
import pandas as pd
import django
from decimal import Decimal

# Add the backend directory to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hesaplama.models import KargoFirma, DesiKgDeger, DesiKgKargoUcret

def import_trendyol_desi_kargo_data():
    """
    Trendyol Desi-Kg ve Kargo Fiyatları Excel dosyasından verileri okuyup veritabanına aktaran fonksiyon.
    
    Bu fonksiyon şunları yapar:
    1. Excel dosyasını okur
    2. İlgili tabloları oluşturur (KargoFirma, DesiKgDeger, DesiKgKargoUcret)
    3. Excel'deki verileri bu tablolara aktarır
    """
    try:
        # Excel dosyasının yolu (projenin kök dizinindeki Excel dosyası)
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 
                                "Trendyol Desi-Kg ve Kargo Fiyatları (Temizlenmiş Hali).xlsx")
        
        # Excel dosyasını pandas ile oku
        df = pd.read_excel(file_path)
        
        # İlk satırı sütun adları olarak kullan
        columns = df.columns.tolist()
        
        # İlk sütun desi/kg değerlerini içerir
        desi_kg_values = df.iloc[:, 0].dropna().tolist()
        
        # Kargo firma isimleri sütun adlarında (ilk sütun hariç)
        kargo_firma_names = columns[1:]
        
        print(f"İşlenecek desi/kg değerleri: {desi_kg_values}")
        print(f"İşlenecek kargo firmaları: {kargo_firma_names}")
        
        # Veritabanını temizle (isteğe bağlı, yorum satırından çıkarılabilir)
        # KargoFirma.objects.all().delete()
        # DesiKgDeger.objects.all().delete()
        # DesiKgKargoUcret.objects.all().delete()
        
        # Kargo firmalarını oluştur
        kargo_firma_objects = {}
        for firma_name in kargo_firma_names:
            firma, created = KargoFirma.objects.get_or_create(firma_ismi=firma_name)
            kargo_firma_objects[firma_name] = firma
            if created:
                print(f"Kargo firması oluşturuldu: {firma_name}")
            else:
                print(f"Var olan kargo firması: {firma_name}")
        
        # Desi/Kg değerlerini oluştur
        desi_kg_objects = {}
        for desi_value in desi_kg_values:
            desi_obj, created = DesiKgDeger.objects.get_or_create(desi_degeri=float(desi_value))
            desi_kg_objects[desi_value] = desi_obj
            if created:
                print(f"Desi/Kg değeri oluşturuldu: {desi_value}")
            else:
                print(f"Var olan Desi/Kg değeri: {desi_value}")
        
        # Kargo ücretlerini oluştur
        created_count = 0
        updated_count = 0
        
        for idx, row in df.iterrows():
            desi_value = row.iloc[0]
            
            # Geçersiz değerleri atla
            if pd.isna(desi_value):
                continue
                
            desi_obj = desi_kg_objects[desi_value]
            
            for firma_name in kargo_firma_names:
                fiyat_value = row[firma_name]
                
                # Geçersiz fiyat değerlerini atla
                if pd.isna(fiyat_value):
                    continue
                
                firma_obj = kargo_firma_objects[firma_name]
                
                # String ise temizle ve sayıya çevir
                if isinstance(fiyat_value, str):
                    fiyat_value = fiyat_value.replace('₺', '').replace('TL', '').strip()
                
                # Decimal'e çevir
                decimal_fiyat = Decimal(str(fiyat_value))
                
                # Kayıt var mı kontrol et
                obj, created = DesiKgKargoUcret.objects.update_or_create(
                    kargo_firma=firma_obj,
                    desi_kg_deger=desi_obj,
                    defaults={'fiyat': decimal_fiyat}
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        
        print(f"Toplam {created_count} yeni kargo ücreti kaydı oluşturuldu.")
        print(f"Toplam {updated_count} var olan kargo ücreti kaydı güncellendi.")
        print("İşlem başarılı bir şekilde tamamlandı.")
        
        return True, "Veri içe aktarımı başarıyla tamamlandı."
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return False, f"Hata: {str(e)}"

if __name__ == "__main__":
    success, message = import_trendyol_desi_kargo_data()
    print(message)
