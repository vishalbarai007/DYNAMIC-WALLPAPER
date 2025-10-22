import requests

def get_weather_category(api_key):
    try:
        res = requests.get(f"http://ip-api.com/json/").json()
        lat, lon = res["lat"], res["lon"]

        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
        data = requests.get(weather_url).json()
        main = data["weather"][0]["main"].lower()

        if "rain" in main:
            return "rainy"
        elif "cloud" in main:
            return "cloudy"
        elif "clear" in main:
            return "sunny"
        else:
            return None
    except Exception as e:
        print(f"❌ Weather fetch failed: {e}")
        return None
