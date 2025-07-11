import requests
from config import API_KEY, CITY

def fetch_weather_data():
    url = f'https://api.openweathermap.org/data/2.5/weather?q={CITY}&appId={API_KEY}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': 'Failed to fetch weather data'}