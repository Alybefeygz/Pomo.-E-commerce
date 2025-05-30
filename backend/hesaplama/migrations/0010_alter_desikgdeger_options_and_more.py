# Generated by Django 5.1.6 on 2025-04-03 13:24

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hesaplama', '0009_update_database_structure'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='desikgdeger',
            options={'verbose_name': 'Desi/Kg Değeri', 'verbose_name_plural': 'Desi/Kg Değerleri'},
        ),
        migrations.AlterModelOptions(
            name='desikgkargoucret',
            options={'verbose_name': 'Desi/Kg Kargo Ücreti', 'verbose_name_plural': 'Desi/Kg Kargo Ücretleri'},
        ),
        migrations.AlterModelOptions(
            name='kargofirma',
            options={'verbose_name': 'Kargo Firması', 'verbose_name_plural': 'Kargo Firmaları'},
        ),
        migrations.AlterField(
            model_name='desikgdeger',
            name='pazar_yeri',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='desi_kg_degerleri', to='hesaplama.pazaryeri'),
        ),
        migrations.AlterField(
            model_name='desikgkargoucret',
            name='pazar_yeri',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kargo_ucretleri', to='hesaplama.pazaryeri'),
        ),
        migrations.CreateModel(
            name='KargoHesaplamaGecmisi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(default='guest@example.com', help_text='Hesaplama yapan kullanıcının email adresi', max_length=254)),
                ('en', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('boy', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('yukseklik', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('net_agirlik', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('hesaplanan_desi', models.DecimalField(decimal_places=2, help_text='(en * boy * yükseklik) / 3000', max_digits=10)),
                ('hesaplanan_desi_kg', models.DecimalField(decimal_places=2, help_text='max(desi, net_agirlik)', max_digits=10)),
                ('yuvarlanmis_desi_kg', models.DecimalField(decimal_places=2, help_text='Yuvarlanmış desi/kg değeri', max_digits=10)),
                ('kargo_ucreti', models.DecimalField(decimal_places=2, help_text='Hesaplanan kargo ücreti', max_digits=10)),
                ('olusturma_tarihi', models.DateTimeField(auto_now_add=True)),
                ('guncelleme_tarihi', models.DateTimeField(auto_now=True)),
                ('kargo_firma', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hesaplama.kargofirma')),
                ('kullanici', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kargo_hesaplamalari', to=settings.AUTH_USER_MODEL)),
                ('pazar_yeri', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='hesaplama.pazaryeri')),
            ],
            options={
                'verbose_name': 'Kargo Hesaplama Geçmişi',
                'verbose_name_plural': 'Kargo Hesaplama Geçmişleri',
                'ordering': ['-olusturma_tarihi'],
            },
        ),
    ]
