import os
import sys
import django
import time

# Django ayarlarını yükle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from hesaplama.models import HesaplamaKategoriler, HesaplamaKomisyonOranlari

def temizle_kategori_verileri():
    """
    HesaplamaKategoriler ve HesaplamaKomisyonOranlari tablolarındaki tüm verileri siler.
    
    Returns:
        tuple: (bool, str) - İşlemin başarılı olup olmadığı ve sonuç mesajı
    """
    try:
        # SQLite veritabanı bağlantısını kapat ve yeniden aç
        connection.close()
        time.sleep(1)  # 1 saniye bekle
        
        # Önce komisyon oranlarını sil (ForeignKey bağlantısı nedeniyle)
        komisyon_sayisi = HesaplamaKomisyonOranlari.objects.all().count()
        HesaplamaKomisyonOranlari.objects.all().delete()
        
        # Sonra kategorileri sil
        kategori_sayisi = HesaplamaKategoriler.objects.all().count()
        HesaplamaKategoriler.objects.all().delete()
        
        return True, f"Veriler başarıyla silindi:\n- {komisyon_sayisi} adet komisyon oranı\n- {kategori_sayisi} adet kategori"
        
    except Exception as e:
        return False, f"Hata oluştu: {str(e)}"

if __name__ == "__main__":
    basarili, mesaj = temizle_kategori_verileri()
    print(mesaj)
    if not basarili:
        sys.exit(1)  # Hata durumunda 1 döndür
    sys.exit(0)  # Başarılı durumda 0 döndür 