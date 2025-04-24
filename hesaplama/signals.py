from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import transaction
from .models import KargoUcretGecmis, KomisyonOraniGecmisi, FiyatHesaplamaGecmisi

def link_previous_calculations(user):
    """
    Verilen kullanıcının email adresine göre önceki işlemlerini hesabına bağlar.
    """
    with transaction.atomic():
        # Kargo ücreti hesaplama geçmişini güncelle
        KargoUcretGecmis.objects.filter(
            email__iexact=user.email,
            kullanici__isnull=True
        ).update(kullanici=user)
        
        # Komisyon oranı hesaplama geçmişini güncelle
        KomisyonOraniGecmisi.objects.filter(
            email__iexact=user.email,
            kullanici__isnull=True
        ).update(kullanici=user)
        
        # Fiyat hesaplama geçmişini güncelle
        FiyatHesaplamaGecmisi.objects.filter(
            email__iexact=user.email,
            kullanici__isnull=True
        ).update(kullanici=user)

@receiver(post_save, sender=get_user_model())
def update_user_calculations_on_save(sender, instance, created, **kwargs):
    """
    Kullanıcı kayıt olduğunda veya güncellendiğinde çalışır.
    """
    link_previous_calculations(instance)

@receiver(user_logged_in)
def update_user_calculations_on_login(sender, user, request, **kwargs):
    """
    Kullanıcı her giriş yaptığında çalışır.
    """
    link_previous_calculations(user) 