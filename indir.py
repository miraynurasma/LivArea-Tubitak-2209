import requests

# Güvenilir bir kaynaktan Türkiye GeoJSON verisini çekiyoruz
url = "https://raw.githubusercontent.com/cihadturhan/tr-geojson/master/tr-cities.json"
response = requests.get(url)

if response.status_code == 200:
    with open('turkiye.json', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("✅ turkiye.json başarıyla oluşturuldu! Şimdi arayüzü çalıştırabilirsin.")
else:
    print("❌ Dosya indirilemedi, lütfen internet bağlantını kontrol et.")