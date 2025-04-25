import os
import sys
import django

# Django ayarlarını yükle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hesaplama.models import Pazaryeri

def pazaryeri_sil(pazaryeri_id):
    """
    Belirtilen ID'ye sahip pazar yerini siler.
    
    Args:
        pazaryeri_id (int): Silinecek pazar yerinin ID değeri
        
    Returns:
        tuple: (bool, str) - İşlemin başarılı olup olmadığı ve sonuç mesajı
    """
    try:
        # Pazar yerini bul
        pazaryeri = Pazaryeri.objects.filter(id=pazaryeri_id).first()
        
        if not pazaryeri:
            return False, f"ID değeri {pazaryeri_id} olan pazar yeri bulunamadı."
        
        # Pazar yeri adını kaydet
        pazaryeri_adi = pazaryeri.pazar_ismi
        
        # Pazar yerini sil
        pazaryeri.delete()
        
        return True, f"'{pazaryeri_adi}' pazar yeri başarıyla silindi."
        
    except Exception as e:
        import traceback
        print(f"Hata oluştu: {str(e)}")
        print(traceback.format_exc())
        return False, f"Hata: {str(e)}"

if __name__ == "__main__":
    # Gittigidiyor pazar yerinin ID değeri
    pazaryeri_id = 14
    
    basarili, mesaj = pazaryeri_sil(pazaryeri_id)
    print(mesaj)
    if not basarili:
        sys.exit(1)  # Hata durumunda 1 döndür
    sys.exit(0)  # Başarılı durumda 0 döndür 