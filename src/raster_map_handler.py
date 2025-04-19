import requests
import pandas as pd
import numpy as np

def fetch_raster_pm25(lat, lon, radius_deg=1.0):
    base_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    bbox = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "pm2_5",
        "past_days": 1
    }
    response = requests.get(base_url, params=bbox)
    data = response.json()

    if "hourly" not in data or "pm2_5" not in data["hourly"]:
        raise ValueError("No PM2.5 data returned")

    df = pd.DataFrame({
        "time": pd.to_datetime(data["hourly"]["time"]),
        "pm2_5": data["hourly"]["pm2_5"]
    })
    df = df.set_index("time").resample("h").mean()
    latest = df["pm2_5"].iloc[-1]

    return latest

def fake_raster_from_point(lat, lon, value, grid_size=1.0, resolution=0.05):
    lats = np.arange(lat - grid_size, lat + grid_size + resolution, resolution)
    lons = np.arange(lon - grid_size, lon + grid_size + resolution, resolution)
    lon_grid, lat_grid = np.meshgrid(lons, lats)

    decay  = np.exp(-((lat_grid - lat)**2 + (lon_grid - lon)**2) / (2 * 0.2**2))
    pm_grid = value * decay

    df_map = pd.DataFrame({
        "latitude": lat_grid.flatten(),
        "longitude": lon_grid.flatten(),
        "value": pm_grid.flatten()
    })
    return df_map

def scale_forecast_raster(df_raster, scale_factor):
    df_forecast = df_raster.copy()
    df_forecast["value"] = df_forecast["value"] * scale_factor
    df_forecast["value"] = df_forecast["value"].clip(0, 500)
    return df_forecast