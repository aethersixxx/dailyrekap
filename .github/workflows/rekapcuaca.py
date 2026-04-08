import requests
from datetime import datetime, timedelta

# ================== KONFIGURASI ==================
TELEGRAM_TOKEN = "8054170482:AAEB4WqoYUkNXt2lz3A3xvPwQ4FDiNyV5KI"      # dari @BotFather
CHAT_ID = "1226199501"               # chat dengan bot lalu ambil ID (bisa pakai getUpdates)
OPENWEATHER_API_KEY = "9b629b666bc571d087d43ed6d17a4e8f"

# Daftar kota HIGH VOLUME Polymarket (update sesekali di https://polymarket.com/predictions/temperature)
CITIES = {
    "Shanghai": {"lat": 31.2304, "lon": 121.4737},
    "Seoul": {"lat": 37.5665, "lon": 126.9780},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "Istanbul": {"lat": 41.0082, "lon": 28.9784},
    "New York City": {"lat": 40.7128, "lon": -74.0060},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Wellington": {"lat": -41.2865, "lon": 174.7762},
    "Ankara": {"lat": 39.9334, "lon": 32.8597},
    # Tambah kota lain di sini kalau volumenya naik (contoh: Taipei, Shenzhen, dll.)
}

# ================================================

def get_open_meteo_high(lat: float, lon: float) -> float | None:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&timezone=auto&forecast_days=2"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return round(data["daily"]["temperature_2m_max"][1], 1)  # index 1 = besok
    except:
        return None

def get_openweather_high(lat: float, lon: float, api_key: str) -> float | None:
    if not api_key:
        return None
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        now = datetime.utcnow()
        tomorrow_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow_end = tomorrow_start + timedelta(days=1)
        max_t = -100
        for item in data.get("list", []):
            item_time = datetime.fromtimestamp(item["dt"], tz=None)
            if tomorrow_start <= item_time < tomorrow_end:
                temp = item["main"].get("temp_max", item["main"]["temp"])
                if temp > max_t:
                    max_t = temp
        return round(max_t, 1) if max_t > -100 else None
    except:
        return None

def main():
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%d %B %Y")

    message = f"🔥 **Rekap Suhu Tertinggi Besok ({tomorrow_date}) – High Volume Polymarket**\n\n"
    message += "Sumber: **Open-Meteo + OpenWeatherMap** (rata-rata 2 model terbaik)\n"
    message += "Tujuan: Prediksi Polymarket lebih presisi\n\n"

    for city, coords in CITIES.items():
        om = get_open_meteo_high(coords["lat"], coords["lon"])
        owm = get_openweather_high(coords["lat"], coords["lon"], OPENWEATHER_API_KEY)
        
        if om is not None and owm is not None:
            avg = round((om + owm) / 2, 1)
            txt = f"`{avg}°C` (OM:{om} OWM:{owm})"
        elif om is not None:
            txt = f"`{om}°C` (Open-Meteo)"
        elif owm is not None:
            txt = f"`{owm}°C` (OpenWeatherMap)"
        else:
            txt = "Gagal mengambil data"
        
        message += f"🌡️ **{city}**: {txt}\n"

    # Kirim Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, json=payload, timeout=10)
    print(f"✅ Rekap besok ({tomorrow_date}) sudah dikirim ke Telegram!")

if __name__ == "__main__":
    main()
