import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

from datetime import datetime


url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 59.9386,
	"longitude": 30.3141,
	"daily": ["temperature_2m_max", "temperature_2m_min", "apparent_temperature_min", "apparent_temperature_max", "wind_speed_10m_max", "daylight_duration", "precipitation_probability_max", "precipitation_hours"],
	"timezone": "Europe/Moscow",
}

def getData():
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    responses = openmeteo.weather_api(url, params = params)
    response = responses[0]

    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
    daily_apparent_temperature_min = daily.Variables(2).ValuesAsNumpy()
    daily_apparent_temperature_max = daily.Variables(3).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(4).ValuesAsNumpy()
    daily_daylight_duration = daily.Variables(5).ValuesAsNumpy()
    daily_precipitation_probability_max = daily.Variables(6).ValuesAsNumpy()
    daily_precipitation_hours = daily.Variables(7).ValuesAsNumpy()

    daily_data = {
        "date": pd.date_range(
            start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
            end =  pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = daily.Interval()),
            inclusive = "left"
        ).tz_convert(response.Timezone().decode())
    }

    daily_data["temperature_2m_max"] = daily_temperature_2m_max
    daily_data["temperature_2m_min"] = daily_temperature_2m_min
    daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
    daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
    daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
    daily_data["daylight_duration"] = daily_daylight_duration
    daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
    daily_data["precipitation_hours"] = daily_precipitation_hours

    daily_dataframe = pd.DataFrame(data = daily_data)

    return daily_dataframe

def getWeatherToday():
    weather = getData().iloc[0]

    data = {
        "today": datetime.now().strftime("%d.%m.%Y"),
        "dayNum": datetime.now().strftime("%A"),
        "maxTemp": round(weather["temperature_2m_max"]),
        "minTemp": round(weather["temperature_2m_min"]),
        "maxTempO": round(weather["apparent_temperature_max"]),
        "minTempO": round(weather["apparent_temperature_min"]),
        "wind": round(weather["wind_speed_10m_max"] / 3.6),
        "dayling": round(weather["daylight_duration"] / (60*60)),
        "PrePercent": int(weather["precipitation_probability_max"]),
        "preHours": int(round(weather["precipitation_hours"])),
        "getUmbrella": False,
    }

    if data['PrePercent'] > 50 and data['preHours']:
        data['getUmbrella'] = True

    return data