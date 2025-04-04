# Generated by Django 5.1.6 on 2025-03-18 19:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DesiKgDeger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desi_degeri', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='KargoFirma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firma_ismi', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='DesiKgKargoUcret',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fiyat', models.DecimalField(decimal_places=2, max_digits=10)),
                ('desi_kg_deger', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kargo_ucretleri', to='hesaplama.desikgdeger')),
                ('kargo_firma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kargo_ucretleri', to='hesaplama.kargofirma')),
            ],
        ),
    ]
