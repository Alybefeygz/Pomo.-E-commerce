# Generated by Django 5.1.6 on 2025-04-04 12:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hesaplama', '0011_hesaplamapazaryeri_hesaplamakategoriler_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hesaplamakomisyonoranlari',
            name='pazar_yeri',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='komisyon_oranlari', to='hesaplama.pazaryeri'),
        ),
        migrations.AlterField(
            model_name='hesaplamakategoriseviyeleri',
            name='pazar_yeri',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='kategori_seviyesi', to='hesaplama.pazaryeri'),
        ),
        migrations.DeleteModel(
            name='HesaplamaPazaryeri',
        ),
    ]
