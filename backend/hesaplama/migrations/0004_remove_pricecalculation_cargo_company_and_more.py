# Generated by Django 5.1.6 on 2025-03-19 13:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hesaplama', '0003_customuser_pricecalculation'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pricecalculation',
            name='cargo_company',
        ),
        migrations.RemoveField(
            model_name='pricecalculation',
            name='product_group',
        ),
        migrations.RemoveField(
            model_name='pricecalculation',
            name='user',
        ),
        migrations.CreateModel(
            name='Hesaplama',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('olusturulma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('toplam_fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kullanici', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hesaplamalar', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Hesaplama',
                'verbose_name_plural': 'Hesaplamalar',
                'ordering': ['-olusturulma_tarihi'],
            },
        ),
        migrations.CreateModel(
            name='Urun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('urun_ismi', models.CharField(max_length=255)),
                ('urun_maliyeti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('paketleme_maliyeti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('trendyol_hizmet_bedeli', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kargo_firmasi', models.CharField(max_length=100)),
                ('kargo_ucreti', models.DecimalField(decimal_places=2, max_digits=10)),
                ('stopaj_degeri', models.DecimalField(decimal_places=2, max_digits=10)),
                ('desi_kg_degeri', models.IntegerField()),
                ('urun_kategorisi', models.CharField(max_length=255)),
                ('komisyon_orani', models.DecimalField(decimal_places=2, max_digits=5)),
                ('komisyon_tutari', models.DecimalField(decimal_places=2, max_digits=10)),
                ('kdv_orani', models.DecimalField(decimal_places=2, max_digits=5)),
                ('kar_orani', models.DecimalField(decimal_places=2, max_digits=5)),
                ('kar_tutari', models.DecimalField(decimal_places=2, max_digits=10)),
                ('satis_fiyati_kdv_haric', models.DecimalField(decimal_places=2, max_digits=10)),
                ('satis_fiyati_kdv_dahil', models.DecimalField(decimal_places=2, max_digits=10)),
                ('hesaplama', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='urunler', to='hesaplama.hesaplama')),
            ],
            options={
                'verbose_name': 'Ürün',
                'verbose_name_plural': 'Ürünler',
            },
        ),
        migrations.DeleteModel(
            name='CustomUser',
        ),
        migrations.DeleteModel(
            name='PriceCalculation',
        ),
    ]
