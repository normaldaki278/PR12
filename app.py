from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'yXcUn6haV3nAcW1UlLUlbe6LEozZwVUu'

def get_weather_data(city, api_key):
    url = f"http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {'apikey': api_key, 'q': city}
    response = requests.get(url, params=params)
    print(f"Location request URL: {response.url}")
    print(f"Location response status: {response.status_code}, headers: {response.headers}, content: {response.text}")
    if response.status_code == 200:
        location_data = response.json()
        if location_data:
            location_key = location_data[0]['Key']
            forecast_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
            forecast_params = {'apikey': api_key, 'metric': 'true', 'details': 'true'}
            forecast_response = requests.get(forecast_url, params=forecast_params)
            print(f"Forecast request URL: {forecast_response.url}")
            print(f"Forecast response status: {forecast_response.status_code}, headers: {forecast_response.headers}, content: {forecast_response.text}")
            if forecast_response.status_code == 200:
                forecast_data = forecast_response.json()
                if 'DailyForecasts' in forecast_data and len(forecast_data['DailyForecasts']) > 0:
                    try:
                        daily_forecast = forecast_data['DailyForecasts'][0]
                        temperature = daily_forecast['Temperature']['Maximum']['Value']
                        wind_speed_kmh = daily_forecast['Day'].get('Wind', {}).get('Speed', {}).get('Value', 0)
                        wind_speed_ms = round(wind_speed_kmh * 0.27778, 2)  # Преобразование в м/с и округление
                        precipitation_probability = daily_forecast['Day'].get('PrecipitationProbability', 0)
                        return {
                            'city': city,
                            'temperature': temperature,
                            'wind_speed': wind_speed_ms,
                            'precipitation_probability': precipitation_probability
                        }
                    except (IndexError, KeyError) as e:
                        print(f"Ошибка извлечения данных: {e}")
                else:
                    print("Ошибка: Неправильная структура данных прогноза.")
            else:
                print(f"Ошибка: Не удалось получить прогноз погоды. Статус: {forecast_response.status_code}")
        else:
            print("Ошибка: Город не найден.")
    else:
        print(f"Ошибка: Не удалось получить данные о местоположении. Статус: {response.status_code}")
    return None

def is_bad_weather(weather_data):
    if weather_data['temperature'] < -5 or weather_data['temperature'] > 35:
        return True
    if weather_data['wind_speed'] > 50:
        return True
    if weather_data['precipitation_probability'] > 70:
        return True
    return False

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_info = None
    error_message = None
    weather_condition = "Хорошая погода"
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            weather_info = get_weather_data(city, API_KEY)
            if weather_info:
                if is_bad_weather(weather_info):
                    weather_condition = "Плохая погода"
            else:
                error_message = 'Ошибка получения данных о погоде. Проверьте название города.'
        else:
            error_message = 'Пожалуйста, введите название города.'
    return render_template('index.html', weather_info=weather_info, error_message=error_message, weather_condition=weather_condition)

if __name__ == '__main__':
    app.run(debug=True)