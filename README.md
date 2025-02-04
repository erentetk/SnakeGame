# Python Snake Game (Çift Yılanlı Savaş)

Bu proje Python ve Pygame kullanılarak geliştirilmiş, iki yılanın karşılıklı mücadele ettiği bir oyundur.
![resim](https://github.com/user-attachments/assets/8911442b-77bf-4bd5-9a1c-36bd9be055f4)


## Özellikler

- İki yılan (Yeşil ve Mavi) aynı anda oynuyor
- Her yılan A* algoritması ile otomatik hareket ediyor
- Her 3 yemde bir rastgele oluşan duvarlar
- Yılanlar birbirleriyle ve duvarlarla çarpışabiliyor
- Detaylı skor sistemi
- Farklı kazanma koşulları:
  - Kafa kafaya çarpışmada uzun olan kazanır
  - Duvara veya kendine çarpan kaybeder
  - Yem için yer kalmazsa yüksek skorlu kazanır

## Gereksinimler

- Python 3.x
- Pygame 2.5.2

## Kurulum

1. Gerekli kütüphaneyi yükleyin:
```bash
pip install -r requirements.txt
```

2. Oyunu çalıştırın:
```bash
python snake_game.py
```

## Nasıl Oynanır

- Oyun otomatik olarak oynanır
- İki yılan aynı anda yemi kapmaya çalışır
- Yılanlar birbirlerinden ve duvarlardan kaçınır
- Her yem 10 puan değerindedir
- Oyun bittiğinde SPACE tuşu ile yeniden başlatılır

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.
