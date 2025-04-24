from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hesaplama', '0008_kargofirma_logo'),
    ]

    operations = [
        # Create pazaryeri table first
        migrations.CreateModel(
            name='Pazaryeri',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pazar_ismi', models.CharField(max_length=100)),
                ('aktif', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Pazar Yeri',
                'verbose_name_plural': 'Pazar Yerleri',
            },
        ),
        
        # Update kargofirma table
        migrations.AddField(
            model_name='kargofirma',
            name='aktif',
            field=models.BooleanField(default=True),
        ),
        
        # Add pazar_yeri field as nullable first
        migrations.AddField(
            model_name='desikgdeger',
            name='pazar_yeri',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='desi_kg_degerleri', to='hesaplama.pazaryeri'),
        ),
        
        # Add pazar_yeri field as nullable first
        migrations.AddField(
            model_name='desikgkargoucret',
            name='pazar_yeri',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='kargo_ucretleri', to='hesaplama.pazaryeri'),
        ),
        
        # Rename fiyat to ucret in desikgkargoucret
        migrations.RenameField(
            model_name='desikgkargoucret',
            old_name='fiyat',
            new_name='ucret',
        ),
        
        # Create pazaryeri_kargofirma table
        migrations.CreateModel(
            name='PazaryeriKargofirma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pazar_yeri', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kargo_firmalari', to='hesaplama.pazaryeri')),
                ('kargo_firma', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pazar_yerleri', to='hesaplama.kargofirma')),
            ],
            options={
                'verbose_name': 'Pazar Yeri Kargo Firması',
                'verbose_name_plural': 'Pazar Yeri Kargo Firmaları',
            },
        ),
    ] 