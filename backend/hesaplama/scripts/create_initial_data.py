import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hesaplama.models import Pazaryeri

def create_initial_data():
    # Pazar yerlerini oluştur
    pazar_yerleri = [
        "Trendyol",
        "Hepsiburada",
        "N11",
        "Amazon",
        "GittiGidiyor"
    ]
    
    for pazar in pazar_yerleri:
        Pazaryeri.objects.get_or_create(
            pazar_ismi=pazar,
            defaults={'aktif': True}
        )
        print(f"{pazar} pazar yeri oluşturuldu.")

if __name__ == '__main__':
    create_initial_data()
    print("Başlangıç verileri başarıyla oluşturuldu!") 