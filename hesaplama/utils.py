from django.db import transaction
from .models import KargoUcretGecmis, KomisyonOraniGecmisi, FiyatHesaplamaGecmisi

def check_and_link_calculations(user, email):
    """
    Hesaplama işleminden önce kullanıcı durumunu kontrol eder ve gerekirse geçmiş hesaplamaları bağlar.
    
    Args:
        user: Request'ten gelen kullanıcı nesnesi
        email: İşlemde kullanılan email adresi
        
    Returns:
        bool: İşlemin başarılı olup olmadığı
    """
    try:
        # Kullanıcı giriş yapmış mı kontrol et
        if user.is_authenticated:
            # Giriş yapan kullanıcının emaili ile işlem emaili eşleşiyor mu kontrol et
            if user.email.lower() != email.lower():
                return False
                
            # Transaction başlat
            with transaction.atomic():
                # Kargo ücreti hesaplama geçmişini güncelle
                KargoUcretGecmis.objects.filter(
                    email__iexact=email,
                    kullanici__isnull=True
                ).update(kullanici=user)
                
                # Komisyon oranı hesaplama geçmişini güncelle
                KomisyonOraniGecmisi.objects.filter(
                    email__iexact=email,
                    kullanici__isnull=True
                ).update(kullanici=user)
                
                # Fiyat hesaplama geçmişini güncelle
                FiyatHesaplamaGecmisi.objects.filter(
                    email__iexact=email,
                    kullanici__isnull=True
                ).update(kullanici=user)
                
        return True
        
    except Exception as e:
        print(f"Hesaplama geçmişi bağlama hatası: {str(e)}")
        return False 