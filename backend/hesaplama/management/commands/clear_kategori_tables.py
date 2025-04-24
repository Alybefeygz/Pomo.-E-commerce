from django.core.management.base import BaseCommand
from hesaplama.models import HesaplamaKategoriSeviyeleri
from django.db import transaction, connection
from django.db.utils import OperationalError

class Command(BaseCommand):
    help = 'HesaplamaKategoriSeviyeleri tablosundaki tüm verileri ve tabloyu siler'

    def handle(self, *args, **kwargs):
        try:
            # Önce verileri sil
            with transaction.atomic():
                # Tabloyu temizle
                seviye_count = HesaplamaKategoriSeviyeleri.objects.all().delete()[0]

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Başarıyla silinen kayıt sayıları:\n'
                        f'- HesaplamaKategoriSeviyeleri: {seviye_count} kayıt\n'
                    )
                )

            # Şimdi tabloyu sil
            with connection.cursor() as cursor:
                try:
                    # SQLite için foreign key kontrolünü geçici olarak devre dışı bırak
                    cursor.execute('PRAGMA foreign_keys=OFF;')
                    
                    # Tabloyu sil
                    cursor.execute('DROP TABLE IF EXISTS hesaplama_kategori_seviyeleri;')
                    
                    # Foreign key kontrolünü tekrar etkinleştir
                    cursor.execute('PRAGMA foreign_keys=ON;')

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\nTablo başarıyla silindi:\n'
                            f'- hesaplama_kategori_seviyeleri'
                        )
                    )
                except OperationalError as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Tablo silinirken bir hata oluştu: {str(e)}'
                        )
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'İşlem sırasında bir hata oluştu: {str(e)}'
                )
            ) 