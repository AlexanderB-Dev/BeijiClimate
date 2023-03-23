import requests
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import os
import pytz
import time as t

print(f"Program started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

API_KEY = 'your_api_key_here'

beijing_tz = pytz.timezone('Asia/Shanghai')

def get_local_time_in_beijing():
    beijing_tz = pytz.timezone('Asia/Shanghai')
    beijing_time = datetime.datetime.now(beijing_tz)
    return beijing_time


def is_time_to_run():
    beijing_time = get_local_time_in_beijing()
    target_time = datetime.time(11, 35)
    target_datetime = beijing_tz.localize(datetime.datetime.combine(beijing_time.date(), target_time))
    return beijing_time >= target_datetime and beijing_time < (target_datetime + datetime.timedelta(minutes=1))


def fetch_data(api_key):
    base_url = 'http://api.openweathermap.org/data/2.5'
    box_coordinates_beijing = '115.5,39.5,117.5,41.5,10'
    box_coordinates_xian = '107.5,33.5,109.5,35.5,10'
    box_coordinates_list = [box_coordinates_beijing, box_coordinates_xian]

    data = []

    for box_coordinates in box_coordinates_list:
        weather_url = f'{base_url}/box/city?bbox={box_coordinates}&appid={api_key}&units=metric'
        weather_response = requests.get(weather_url)

        if weather_response.status_code == 200:
            weather_data = weather_response.json()

            for city_data in weather_data['list']:
                city = city_data['name']
                lat = city_data['coord']['Lat']
                lon = city_data['coord']['Lon']
                temperature = city_data['main']['temp']

                pollution_url = f'{base_url}/air_pollution?lat={lat}&lon={lon}&appid={api_key}'
                pollution_response = requests.get(pollution_url)

                if pollution_response.status_code == 200:
                    pollution_data = pollution_response.json()
                    pm25 = pollution_data['list'][0]['components']['pm2_5']

                    data.append({'city': city, 'temperature': temperature, 'pm25': pm25})

    return data


def collect_and_save_data():
    data = fetch_data(api_key)
    df = pd.DataFrame(data)

    pearson_coeff, p_value = pearsonr(df['temperature'], df['pm25'])
    print(f"Pearson correlation coefficient: {pearson_coeff:.2f}")
    print(f"P-value: {p_value:.5f}")

    current_timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'data_{current_timestamp}.csv'
    df.to_csv(csv_filename, index=False)

    print(f"Data saved to {csv_filename}")


def run_daily():
    print("Starting data collection...")
    collect_and_save_data()
    print("Data collection completed!")

if not os.path.exists('programstart_data.csv'):
    data = fetch_data(api_key)
    programstart_df = pd.DataFrame(data)
    programstart_df.to_csv('programstart_data.csv', index=False)
    print("Real data saved to 'programstart_data.csv'.")

daily_task_done = False
while True:
    beijing_time = get_local_time_in_beijing()
    print(f"Current Beijing time: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')}")
    if is_time_to_run() and not daily_task_done:
        run_daily()
        daily_task_done = True
    elif not is_time_to_run():
        daily_task_done = False
    t.sleep(60)
