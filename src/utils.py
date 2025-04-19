from geopy.geocoders import Nominatim

def get_coords_from_city(city_name):
    geolocator = Nominatim(user_agent="aqi_forecaster")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError(f"Could not geocode city: {city_name}")
