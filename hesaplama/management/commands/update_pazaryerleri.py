from django.core.management.base import BaseCommand
from hesaplama.models import Pazaryeri

class Command(BaseCommand):
    help = 'Pazaryeri tablosunu günceller'

    def handle(self, *args, **options):
        # Eski pazaryerleri
        eski_pazaryerleri = [
            'Amazon',
            'GittiGidiyor',
            'Hepsiburada',
            'N11',
            'Trendyol'
        ]
        
        # Yeni pazaryerleri
        yeni_pazaryerleri = [
            'Trendyol',
            'Hepsiburada',
            'N11',
            'GittiGidiyor',
            'Pazarama',
            'İdefix',
            'PTT',
            'Çiçek Sepeti'
        ]
        
        # Eski pazaryerlerini sil
        for eski_pazaryeri in eski_pazaryerleri:
            try:
                Pazaryeri.objects.filter(pazar_ismi=eski_pazaryeri).delete()
                self.stdout.write(self.style.SUCCESS(f'{eski_pazaryeri} silindi'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'{eski_pazaryeri} silinirken hata oluştu: {str(e)}'))
        
        # Yeni pazaryerlerini ekle
        for yeni_pazaryeri in yeni_pazaryerleri:
            try:
                # Eğer pazaryeri zaten varsa ekleme
                if not Pazaryeri.objects.filter(pazar_ismi=yeni_pazaryeri).exists():
                    Pazaryeri.objects.create(pazar_ismi=yeni_pazaryeri)
                    self.stdout.write(self.style.SUCCESS(f'{yeni_pazaryeri} eklendi'))
                else:
                    self.stdout.write(self.style.WARNING(f'{yeni_pazaryeri} zaten mevcut'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'{yeni_pazaryeri} eklenirken hata oluştu: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Pazaryeri tablosu başarıyla güncellendi')) 