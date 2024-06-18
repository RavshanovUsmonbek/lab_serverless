import requests


class OpenMeteoClient:
    def __init__(self):
        self.url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    
    
    def get_data(self):
        response = requests.get(self.url)    
        return response
