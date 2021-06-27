import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

class OWM_forecast:
    """
    Class refers by API to OpenWeatherMap using user API key
    capable of returning
    wind
    clouds
    visibility
    sunrise and sunset GMT time
    temperature in degrees Centigrade
    """

    def __init__(self, apikey):
        """
        :param apikey: API key from https://home.openweathermap.org/api_keys
        (needs about 1 hr to initialize)
        """
        self.apikey = apikey
        self.weather = dict()
        self.city = ''

    def req_weather(self, city='Moscow'):
        self.city = city
        r = requests.get(f'http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.apikey}')
        if r.status_code == 200:

            self.weather = json.loads(r.text)

    def get_wind(self):
        return self.weather.get('wind')

    def get_clouds(self):
        return self.weather.get('weather')[0]['description']

    def get_temp(self, how='act'):
        temp = {
            'act' : self.weather.get('main')['temp'] - 273,
            'feels' : self.weather.get('main')['feels_like'] - 273
        }
        return temp[how]

    def get_visibility(self):
        return self.weather.get('visibility')

    def get_sun(self, type='rise'):
        system = self.weather.get('sys')
        sun = {
            'rise': system['sunrise'],
            'set' : system['sunset']
            }
        return datetime.fromtimestamp(sun[type])

    def __str__(self):
        try:
            clouds = self.get_clouds()
            wind = self.get_wind()
            visibility = self.get_visibility()
            system = self.weather.get('sys')
            sunrise = self.get_sun('rise')
            sunset = self.get_sun('set')
            temp = self.get_temp('act')
            temp_feels = self.get_temp('feels')
            return(
                f"City: {self.city}\n"
                f"Weather: {clouds} visibility {visibility} m\n"
                f"Wind is from {wind['deg']} degrees {wind['speed']} m/s gusting {wind['gust']} m/s\n"
                f"Temperature is {int(temp)} feels like {int(temp_feels)}\n"
                f"Sunrise is {sunrise} GMT sunset is {sunset} GMT\n"
            )
        except BaseException as e:
            print(e)
            return ''


if __name__ == '__main__':
    load_dotenv()
    weather = OWM_forecast(os.getenv('OWM_APIKEY'))
    user_input = input('Enter city name: ')
    weather.req_weather(user_input)
    print(weather)