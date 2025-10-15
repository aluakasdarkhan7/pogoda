from datetime import datetime
import requests
from django.shortcuts import render

API_KEY = '88344296624c4734a40103525251510'

from typing import List, Dict, Optional
from datetime import datetime
import requests

def format_time(date_str: str) -> str:
    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    return dt.strftime('%d %b, %H:%M').replace('.', '')

def weather_view(request):
    city: str = request.POST.get('city', 'Almaty')
    error: Optional[str] = None
    weather: Optional[Dict] = None
    hourly: List[Dict] = []
    daily: List[Dict] = []

    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=5&lang=ru"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if 'error' in data:
            error = data['error'].get('message', 'Ошибка получения данных')
        else:
            location = data['location']
            current = data['current']
            forecast_days = data['forecast']['forecastday']

            weather = {
                'city': location['name'],
                'temp': current['temp_c'],
                'feels_like': current['feelslike_c'],
                'humidity': current['humidity'],
                'wind': current['wind_kph'],
                'description': current['condition']['text'],
                'icon': 'https:' + current['condition']['icon'],
                'last_updated': format_time(current['last_updated']),
            }

            now = datetime.strptime(current['last_updated'], '%Y-%m-%d %H:%M')
            # Объединяем часы и фильтруем
            hours_all = forecast_days[0]['hour'] + forecast_days[1]['hour']
            filtered_hours = [h for h in hours_all if datetime.strptime(h['time'], '%Y-%m-%d %H:%M') >= now]

            for hour in filtered_hours[:12]:
                hour_time = datetime.strptime(hour['time'], '%Y-%m-%d %H:%M').strftime('%H:%M')
                hourly.append({
                    'time': hour_time,
                    'temp': hour['temp_c'],
                    'description': hour['condition']['text'],
                    'icon': 'https:' + hour['condition']['icon'],
                })

            for day in forecast_days[:5]:
                day_date = datetime.strptime(day['date'], '%Y-%m-%d').strftime('%d %b').replace('.', '')
                daily.append({
                    'date': day_date,
                    'maxtemp': day['day']['maxtemp_c'],
                    'mintemp': day['day']['mintemp_c'],
                    'description': day['day']['condition']['text'],
                    'icon': 'https:' + day['day']['condition']['icon'],
                })

    except requests.RequestException:
        error = "Ошибка при запросе данных о погоде. Попробуйте позже."
    except Exception:
        error = "Не удалось получить данные о погоде."

    return render(request, 'forecast/weather.html', {
        'weather': weather,
        'hourly': hourly,
        'daily': daily,
        'error': error,
    })
