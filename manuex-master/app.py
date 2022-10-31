from datetime import datetime
from doctest import set_unittest_reportflags
from flask import Flask, render_template, url_for, request, redirect
import weather
from controller import Controller

app = Flask(__name__)

# Ideally this should be in a file or database
threshold: int = 45
water_amount: int = 50
location: str = 'Eindhoven'
sensor_moisture = 0
#moisture_value: int = 0


@app.route('/')
def index():
    global location
    try:
        weather_data.update(location)
    except (ValueError, ConnectionError) as ex:
        return render_template('error.html', error=ex)

    return render_template('index.html', data=weather_data, sensor_moisture=sensor_moisture)


@app.route('/forecast')
def forecast():
    global location
    try:
        weather_data.update(location)
    except (ValueError, ConnectionError) as ex:
        return render_template('error.html', error=ex)

    return render_template('forecast.html', data=weather_data)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    global threshold
    global water_amount
    global location

    print(threshold, water_amount)

    if request.method == 'POST':
        location = request.form["location"]
        threshold = request.form["threshold"]
        water_amount = request.form["water-amount"]

    return render_template('settings.html', threshold=threshold, water_amount=water_amount, location=location)


@app.route('/base', methods=['POST'])
def display():
    global sensor_moisture
    sensor_moisture = request.get_data()
    moisture_value = int(sensor_moisture.decode("utf-8"))
    print(moisture_value)
    weather_data.update(location)
    return str(Controller.make_decision(weather_data.forecast, moisture_value, threshold))


@app.route('/override')
def override():
    last_watered = datetime.now()

    if request.method == 'POST':
        if request.form.get('action') == 'VALUE':
            pass

    return render_template('override.html', last_watered=last_watered)


if __name__ == "__main__":
    try:
        weather_data = weather.WeatherAPI(
            location, '2096fe218663d046a3a37855c4aea57f')
    except (ValueError, ConnectionError) as ex:
        print('Cannot start application')
        print(ex)
        exit()

    app.run(host='0.0.0.0', port=5000, debug=False)
