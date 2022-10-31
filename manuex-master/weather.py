from datetime import datetime
from typing import Any, Dict, List
from requests import get, ConnectionError


class DataPoint:
    """
    Represents a single data point retrieved from the API.
    The data point can be either current weather or one of the forecast time steps.
    It contains all of the attributes deemed necessary for the forecast module.
    """
    dt: datetime
    temp: float
    humidity: int
    id: int
    description: str
    icon: str
    city_name: str
    rain_last_hour: float
    rain_three_hours: float

    def __init__(self, json: Dict[str, Any]) -> None:
        """Not all of the attributes are always present in the data.
        The attributes that are not present are set to empty values.

        Args:
            json (Dict)): JSON current weather data retruned from OpenWeatherMap API

        Returns:
            None
        """
        self.dt = datetime.fromtimestamp(json['dt'])
        self.temp = json.get('main', {})['temp']
        self.humidity = json.get('main', {})['humidity']
        self.id = json.get('weather', [])[0]['id']
        self.description = json.get('weather', [])[0]['description']
        self.icon = json.get('weather', [])[0]['icon']
        self.city_name = json.get('name', {})
        self.rain_last_hour = json.get('rain', {}).get('1h', {})
        self.rain_three_hours = json.get('rain', {}).get('3h', {})


class Forecast:
    """Represents a forecast as a list of data points retrieved from the API.
    Each data point represents a single time step.
    """
    data: List[DataPoint]

    def __init__(self, json: Dict) -> None:
        """Initializes the forecast object with a list of data points.
        Automatically populates the list from the list contained in the response.

        Args:
            json (Dict)): JSON forecast data retruned from OpenWeatherMap API

        Returns:
            None
        """
        self.data = [DataPoint(i) for i in json['list']]


class WeatherAPI:
    """
    Contains all the data weather data and methods
    for retrieving and updating that data.
    """
    current: DataPoint
    forecast: Forecast

    def __init__(self, location_name: str, api_key: str, units: str = 'metric', count: int = 8) -> None:
        """Initializes the weather API object with the current weather and forecast data.
        Units are metric by default and the forcast returrns 8 time steps (24 hours).

        Args:
            location_name (str): Name of the location to get weather for
            api_key (str): OpenWeatherMap API key
            units(str) [Optioanl]: Units of the weather data. Default is metric
            count (int) [Optional]: Number of time steps in the forecast. Default is 8 (24 hours)

        Errors:
            ValueError: If the response from the API is not valid
            ConnectionError: If the API is not reachable
        """
        self.location_name = location_name
        self.api_key = api_key
        self.units = units
        self.count = count
        self.update(self.location_name)

    def update(self, location: str) -> None:
        """Updates the current weather and forecast data."""
        self.get_weather(location, self.api_key,
                         self.units, self.count)

    def get_weather(self, location_name: str, api_key: str, units: str, count) -> None:
        """
        Makes a GET request to the OpenWeatherMap API and retrieves the current weather and forecast form different endpoints.

        Args:
            location_name (str): Name of the location to get weather for

        Returns:
            None

        Errors:
            ValueError: If the response from the API is not valid
        """
        try:
            current = get(
                f'https://api.openweathermap.org/data/2.5/weather?q={location_name}&appid={api_key}&units={units}', timeout=5)
            forecast = get(
                f'https://api.openweathermap.org/data/2.5/forecast?q={location_name}&appid={api_key}&units={units}&cnt={count}', timeout=5)
        except ConnectionError:
            raise

        current_json = current.json()
        forecast_json = forecast.json()

        if not current_json or not forecast_json or current_json['cod'] != 200 or forecast_json['cod'] != '200':
            raise ValueError(
                f"""One or more of the jason responses is not valid. They are not with response code 200.
                    Current response code: {current_json.get('cod', 'json is empty')}
                    Forecast response code: {forecast_json.get('cod', 'json is empty')}""")

        self.current = DataPoint(current_json)
        self.forecast = Forecast(forecast_json)
