from django.core.management.base import BaseCommand
from hesaplama.models import KargoFirma

class Command(BaseCommand):
    help = 'Veritabanında olması gereken kargo firmalarını oluşturur veya günceller'

    def handle(self, *args, **kwargs):
        # Olması gereken kargo firmaları listesi
        required_firms = [
            'HepsiJET',
            'HepsiJET XL',
            'Aras',
            'MNG',
            'Yurtiçi',
            'Sürat',
            'Kolay Gelsin',
            'PTT',
            'Horoz',
            'Ceva',
            'Borusan',
            'TEX'
        ]

        # Her bir firma için kontrol et ve oluştur/güncelle
        for firma_ismi in required_firms:
            firma, created = KargoFirma.objects.get_or_create(
                firma_ismi=firma_ismi,
                defaults={'aktif': True}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Kargo firması oluşturuldu: {firma_ismi}')
                )
            else:
                # Firma adı farklıysa güncelle
                if firma.firma_ismi != firma_ismi:
                    firma.firma_ismi = firma_ismi
                    firma.save()
                    self.stdout.write(
                        self.style.SUCCESS(f'Kargo firması güncellendi: {firma_ismi}')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Kargo firması zaten mevcut: {firma_ismi}')
                    )

        # Veritabanında olmaması gereken firmaları bul
        existing_firms = set(KargoFirma.objects.values_list('firma_ismi', flat=True))
        required_firms_set = set(required_firms)
        
        # Olmaması gereken firmaları sil
        firms_to_delete = existing_firms - required_firms_set
        if firms_to_delete:
            KargoFirma.objects.filter(firma_ismi__in=firms_to_delete).delete()
            for firma in firms_to_delete:
                self.stdout.write(
                    self.style.SUCCESS(f'Kargo firması silindi: {firma}')
                )

        self.stdout.write(self.style.SUCCESS('Kargo firmaları kontrolü tamamlandı.')) 