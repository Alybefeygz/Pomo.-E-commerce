# Generated by Django 5.1.6 on 2025-04-22 14:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hesaplama', '0015_alter_kategoriyolu_ad_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kategoriyolu',
            name='ad',
            field=models.CharField(help_text='Kategori yolu adı', max_length=255),
        ),
        migrations.AlterField(
            model_name='kategoriyolu',
            name='komisyon_orani',
            field=models.DecimalField(decimal_places=2, help_text='Komisyon oranı yüzdesi', max_digits=5),
        ),
        migrations.AlterField(
            model_name='kategoriyolu',
            name='pazar_yeri',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kategori_yollari', to='hesaplama.pazaryeri'),
        ),
        migrations.AlterField(
            model_name='kategoriyolu',
            name='ust_kategori',
            field=models.ForeignKey(blank=True, help_text='Üst kategori yolu referansı', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alt_kategoriler', to='hesaplama.kategoriyolu'),
        ),
        migrations.AlterModelTable(
            name='kategoriyolu',
            table='kategori_yollari',
        ),
        migrations.CreateModel(
            name='FiyatBelirleme',
            fields=[
                ('urun_id', models.AutoField(primary_key=True, serialize=False)),
                ('urun_ismi', models.CharField(max_length=100)),
                ('urun_maliyeti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paketleme_maliyeti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('trendyol_hizmet_bedeli', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kargo_firmasi', models.CharField(max_length=50)),
                ('kargo_ucreti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stopaj_degeri', models.DecimalField(decimal_places=2, max_digits=10)),
                ('desi_kg_degeri', models.DecimalField(decimal_places=2, max_digits=10)),
                ('urun_kategorisi', models.TextField()),
                ('komisyon_orani', models.DecimalField(decimal_places=2, max_digits=5)),
                ('komisyon_tutari', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kdv_orani', models.DecimalField(decimal_places=2, max_digits=5)),
                ('kar_orani', models.DecimalField(decimal_places=2, max_digits=5)),
                ('kar_tutari', models.DecimalField(decimal_places=2, max_digits=10)),
                ('satis_fiyati_kdv_haric', models.DecimalField(decimal_places=2, max_digits=10)),
                ('satis_fiyati_kdv_dahil', models.DecimalField(decimal_places=2, max_digits=10)),
                ('hesaplama', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fiyat_belirlemeler', to='hesaplama.hesaplamalar')),
            ],
            options={
                'verbose_name': 'Fiyat Belirleme',
                'verbose_name_plural': 'Fiyat Belirlemeler',
            },
        ),
    ]
