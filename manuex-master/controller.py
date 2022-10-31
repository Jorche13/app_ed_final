import weather


class Controller:

    @staticmethod
    def make_decision(forecast: weather.Forecast, sensor_moisture: int, moisture_treshlod: int, lookahead_hours: int = 3) -> bool:

        assert 3 <= lookahead_hours < 120, 'Cannot look ahead more than 5 days'

        # Convert hours to time steps
        lookahead_time_steps: int = lookahead_hours // 3
        total_rainfall: float = 0
        max_temp: float = 0
        max_humidity: int = 0

        # Accumulate forecast data
        for time_step in forecast.data[:lookahead_time_steps]:
            if time_step.rain_three_hours:
                total_rainfall += time_step.rain_three_hours

            if time_step.temp > max_temp:
                max_temp = time_step.temp

            if time_step.humidity > max_humidity:
                max_humidity = time_step.humidity

        # Accoring to very qucik skim of a google search, plants need 0.45mm of water per 3 hours hence the 0.45
        if sensor_moisture < moisture_treshlod:
            if total_rainfall < 0.45 * lookahead_time_steps:
                return True
        else:
            if max_temp > 30:
                if total_rainfall < 0.45 * lookahead_time_steps and sensor_moisture < 60:
                    return True

        return False
