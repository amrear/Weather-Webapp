import requests  # For web APIs.
import random
import os  # For random wallpaper each time.
import sys
from flask import Flask, render_template, request

# A list of backgrounds that you want in your web page.
# You can add more or remove some in `static/background` or changing the specified path.
background_names = os.listdir(os.path.join(os.getcwd(), "static/backgrounds"))

try:
    # Put the api key that you get in http://openweathermap.org
    APPID = os.environ["openweather_appid"]
except:
    Exception("Make sure you've set the required environment variables")
    sys.exit(1)

def get_location(ip):
    """
    Finds geographical location based on the IP address that was passed to it by the help of a wreb api.
    This function is only called when the location is not provided by the user.
    """
    ip_location = requests.get(f"http://ip-api.com/json/{ip}").json()
    if ip_location["status"] == "success":
        return ip_location["city"]


def get_weather(city, units):
    """
    Fetches the data about the weather based on location if it finds any, then returns it in the form of a dictionary.
    :param city: The city of your choise which you want the weather of
    :param units: can be ether `metric` or `imperial` units
    """
    weather_api = requests.get("http://api.openweathermap.org/data/2.5/weather",          # Requests the weather API
                               params={"q": city, "units": units, "appid": APPID}).json()

    if weather_api.get("message") == "city not found":
        return None

    if not units == "metric" and not units == "imperial":
        return None

    resaults = {
        "temp": f"{weather_api['main']['temp']} °C" if units == "metric" else f"{weather_api['main']['temp']} °F",
        "temp_min": f"{weather_api['main']['temp_min']} °C" if units == "metric" else f"{weather_api['main']['temp_min']} °F",
        "temp_max": f"{weather_api['main']['temp_max']} °C" if units == "metric" else f"{weather_api['main']['temp_max']} °F",
        "description": weather_api["weather"][0]["description"].title(),
        "pressure": f"{weather_api['main']['pressure']}hPa",
        "humidity": f"{weather_api['main']['humidity']}%",
        "visibility": f"{weather_api['visibility']}m",
        "wind_speed": f"{weather_api['wind']['speed']}meters/s" if units == "metric" else f"{weather_api['wind']['speed']}miles/h"
    }

    return resaults


app = Flask(__name__)


@app.route("/")
def index():
    city = request.args.get("city", get_location(request.remote_addr))   # Gets the city that user provided. If nothing is provided,
                                                                         # the location will be based on clients IP address.
    
    units = request.args.get("units")        # Checks to see what unit is specified by the user
                                             # If nothing is provided, default is `metric`

    data = get_weather(city, units)

    if not data:
        return render_template("city_not_found.html", background=random.choice(background_names))

    return render_template("index.html", background=random.choice(background_names), city=city.title(), data=data)


if __name__ == "__main__":
    app.run(debug=True)
