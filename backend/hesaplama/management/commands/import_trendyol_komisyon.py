import os
import pandas as pd
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from hesaplama.models import Kategori, AltKategori, UrunGrubu, KomisyonOrani


class Command(BaseCommand):
    help = 'Trendyol Kategori Komisyon Oranları Excel dosyasından verileri içe aktarır'

    def handle(self, *args, **options):
        try:
            # Excel dosyasının yolu - projenin kök dizininde (backend klasörünün bir üst dizini)
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 
                               '..',  # Backend klasöründen bir üst dizine çık
                               'Trendyol Kategori Komisyon Oranları (Temizlenmiş Hali).xlsx')
            
            # Yolun mutlak olduğundan emin ol
            file_path = os.path.abspath(file_path)
            
            self.stdout.write(f"Excel dosyası yolu: {file_path}")
            
            # Excel dosyasını oku
            df = pd.read_excel(file_path)
            
            # Sütun adlarını göster
            self.stdout.write(f"Excel sütun adları: {list(df.columns)}")
            
            # İlk 5 satırı göster
            self.stdout.write("İlk 5 satır:")
            self.stdout.write(str(df.head()))
            
            # Sütunları doğru şekilde belirle - Excel yapısındaki değişiklikler nedeniyle sütun indekslerini kullanalım
            # Gerçek kolon yapısı: No, Kategori, Alt Kategori, Ürün Grubu, Komisyon Oranı
            kategori_column = 'Kategori'
            alt_kategori_column = 'Alt Kategori'
            urun_grubu_column = 'Ürün Grubu'
            komisyon_column = 'Kategori Komisyon % (KDV Dahil)'
            
            self.stdout.write(f"Kategori Sütunu: {kategori_column}")
            self.stdout.write(f"Alt Kategori Sütunu: {alt_kategori_column}")
            self.stdout.write(f"Ürün Grubu Sütunu: {urun_grubu_column}")
            self.stdout.write(f"Komisyon Oranı Sütunu: {komisyon_column}")
            
            # Benzersiz kategori sayısını göster
            unique_categories = df[kategori_column].nunique()
            self.stdout.write(f"Benzersiz kategori sayısı: {unique_categories}")
            
            with transaction.atomic():
                kategori_objs = {}
                alt_kategori_objs = {}
                
                # Kategorileri oluştur
                for idx, row in df.iterrows():
                    kategori_adi = str(row[kategori_column]).strip()
                    
                    if kategori_adi not in kategori_objs:
                        kategori, created = Kategori.objects.get_or_create(kategori_adi=kategori_adi)
                        kategori_objs[kategori_adi] = kategori
                        self.stdout.write(f"Kategori oluşturuldu: {kategori_adi}")
                
                # Alt kategorileri oluştur
                for idx, row in df.iterrows():
                    kategori_adi = str(row[kategori_column]).strip()
                    alt_kategori_adi = str(row[alt_kategori_column]).strip()
                    
                    if alt_kategori_adi and kategori_adi in kategori_objs:
                        key = f"{kategori_adi} > {alt_kategori_adi}"
                        
                        if key not in alt_kategori_objs:
                            alt_kategori, created = AltKategori.objects.get_or_create(
                                alt_kategori_adi=alt_kategori_adi,
                                kategori=kategori_objs[kategori_adi]
                            )
                            alt_kategori_objs[key] = alt_kategori
                            self.stdout.write(f"Alt kategori oluşturuldu: {kategori_adi} > {alt_kategori_adi}")
                
                # Ürün grupları ve komisyon oranları oluştur
                for idx, row in df.iterrows():
                    try:
                        kategori_adi = str(row[kategori_column]).strip()
                        alt_kategori_adi = str(row[alt_kategori_column]).strip()
                        urun_grubu_adi = str(row[urun_grubu_column]).strip()
                        
                        alt_kategori_key = f"{kategori_adi} > {alt_kategori_adi}"
                        
                        if alt_kategori_key in alt_kategori_objs and urun_grubu_adi:
                            # Komisyon oranını dönüştür - hata işleme ile
                            try:
                                komisyon_str = str(row[komisyon_column]).strip()
                                
                                # Yüzde işareti varsa kaldır
                                if '%' in komisyon_str:
                                    komisyon_str = komisyon_str.replace('%', '').strip()
                                
                                # Virgül yerine nokta kullan
                                if ',' in komisyon_str:
                                    komisyon_str = komisyon_str.replace(',', '.')
                                
                                # Boş kontrolü
                                if not komisyon_str or komisyon_str == 'nan':
                                    self.stdout.write(self.style.WARNING(f"Boş komisyon oranı: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi}"))
                                    continue
                                    
                                # Sayıya dönüştür
                                komisyon_float = float(komisyon_str)
                                
                                # 0-1 aralığı kontrolü (1'den büyükse yüzde olarak kabul et)
                                if komisyon_float > 1:
                                    komisyon_float = komisyon_float / 100
                                
                                komisyon_orani = Decimal(str(komisyon_float))
                                
                                urun_grubu, created = UrunGrubu.objects.get_or_create(
                                    urun_grubu_adi=urun_grubu_adi,
                                    alt_kategori=alt_kategori_objs[alt_kategori_key]
                                )
                                
                                KomisyonOrani.objects.get_or_create(
                                    komisyon_orani=komisyon_orani,
                                    urun_grubu=urun_grubu
                                )
                                
                                self.stdout.write(f"Ürün grubu oluşturuldu: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi}")
                                
                            except (ValueError, InvalidOperation) as e:
                                self.stdout.write(self.style.ERROR(
                                    f"Komisyon oranı dönüştürme hatası: {row[komisyon_column]} - {e}, "
                                    f"Satır: {kategori_adi} > {alt_kategori_adi} > {urun_grubu_adi}"
                                ))
                                
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Hata oluştu: {[type(e)]}, Satır: {idx+1}"))
                        self.stdout.write(self.style.ERROR(f"Hata detayı: {str(e)}"))
            
            self.stdout.write(self.style.SUCCESS('Trendyol kategori komisyon oranları başarıyla içe aktarıldı.'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Komut yürütülürken hata oluştu: {str(e)}")) 