from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = 'sagHHWn7YOtL9FnwqDoXFyrxZljoRdNA'

def get_weather_data(cities, api_key):
    weather_data_list = []
    for city in cities:
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
                            weather_data_list.append({
                                'city': city,
                                'temperature': temperature,
                                'wind_speed': wind_speed_ms,
                                'precipitation_probability': precipitation_probability
                            })
                        except (IndexError, KeyError) as e:
                            print(f"Ошибка извлечения данных для города {city}: {e}")
                    else:
                        print(f"Ошибка: Неправильная структура данных прогноза для города {city}.")
                else:
                    print(f"Ошибка: Не удалось получить прогноз погоды для города {city}. Статус: {forecast_response.status_code}")
            else:
                print(f"Ошибка: Город {city} не найден.")
        else:
            print(f"Ошибка: Не удалось получить данные о местоположении для города {city}. Статус: {response.status_code}")
    return weather_data_list

def is_bad_weather(weather_data):
    conditions = []
    if weather_data['temperature'] < -5:
        conditions.append("очень холодно")
    elif weather_data['temperature'] > 35:
        conditions.append("очень жарко")
    
    if weather_data['wind_speed'] > 50:
        conditions.append("сильный ветер")
    
    if weather_data['precipitation_probability'] > 70:
        conditions.append("высокая вероятность осадков")
    
    return conditions

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_info = []
    error_message = None
    if request.method == 'POST':
        city1 = request.form.get('city1')
        city2 = request.form.get('city2')
        if city1 and city2:
            city_list = [city1.strip(), city2.strip()]
            weather_info = get_weather_data(city_list, API_KEY)
            if weather_info:
                for weather in weather_info:
                    conditions = is_bad_weather(weather)
                    if conditions:
                        weather['condition'] = "Плохая погода: " + ", ".join(conditions)
                    else:
                        weather['condition'] = "Хорошая погода"
            else:
                error_message = 'Ошибка получения данных о погоде. Проверьте названия городов.'
        else:
            error_message = 'Пожалуйста, введите названия обоих городов.'
    return render_template('index.html', weather_info=weather_info, error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
