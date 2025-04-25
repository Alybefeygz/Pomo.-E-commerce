import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from hesaplama.models import KargoFirma, PazaryeriKargofirma, DesiKgKargoUcret, DesiKgDeger

# Verileri sil
DesiKgKargoUcret.objects.all().delete()
DesiKgDeger.objects.all().delete()
PazaryeriKargofirma.objects.all().delete()
KargoFirma.objects.all().delete()

print("Tüm veriler başarıyla silindi!") 