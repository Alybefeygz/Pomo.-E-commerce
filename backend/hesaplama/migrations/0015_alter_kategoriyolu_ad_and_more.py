# Generated by Django 5.1.6 on 2025-04-22 12:05

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hesaplama', '0014_kategoriyolu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kategoriyolu',
            name='ad',
            field=models.CharField(max_length=255, verbose_name='Kategori Yolu Adı'),
        ),
        migrations.AlterField(
            model_name='kategoriyolu',
            name='komisyon_orani',
            field=models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Komisyon Oranı (%)'),
        ),
        migrations.AlterField(
            model_name='kategoriyolu',
            name='pazar_yeri',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kategori_yollari', to='hesaplama.pazaryeri', verbose_name='Pazar Yeri'),
        ),
        migrations.AlterField(
            model_name='kategoriyolu',
            name='ust_kategori',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='alt_kategoriler', to='hesaplama.kategoriyolu', verbose_name='Üst Kategori'),
        ),
        migrations.AlterModelTable(
            name='kategoriyolu',
            table='kategori_yolu',
        ),
        migrations.DeleteModel(
            name='FiyatBelirleme',
        ),
    ]
