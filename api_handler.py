import requests

BASE_URL = "https://api.openaq.org/v2/latest"

def fetch_aqi_data(city=None, lat=None, lon=None, parameters=["pm25", "pm10", "no2", "o3"]):
    if city:
        query = {"city": city, "limit": 100, "parameter": parameters}
    elif lat and lon:
        query = {"coordinates": f"{lat},{lon}", "limit": 100, "parameter": parameters}
    else:
        raise ValueError("Provide either city or (lat, lon)")

    response = requests.get(BASE_URL, params=query)
    data = response.json()

    results = {}
    for item in data.get("results", []):
        for measurement in item.get("measurements", []):
            param = measurement.get("parameter")
            value = measurement.get("value")
            unit = measurement.get("unit")
            if param in parameters:
                results[param] = (value, unit)

    return results