import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_from_openaq_v3(lat, lon, days=30, radius_m=25000):
    end = datetime.utcnow()
    start = end - timedelta(days=days)

    url = "https://api.openaq.org/v3/measurements/nearest"
    params = {
        "coordinates": f"{lat},{lon}",
        "radius": radius_m,
        "parameter": "pm25",
        "date_from": start.isoformat(),
        "date_to": end.isoformat(),
        "limit": 10000,
        "sort": "desc"
    }

    r = requests.get(url, params=params)
    data = r.json()
    results = data.get("results", [])

    if not results:
        raise ValueError("No PM2.5 data found from OpenAQ nearby.")

    records = []
    for item in results:
        records.append({
            "datetime": item["date"]["utc"],
            "value": item["value"]
        })

    df = pd.DataFrame(records)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    full_index = pd.date_range(start=df.index.min(), end=df.index.max(), freq="H")
    df = df.reindex(full_index)
    df["value"] = df["value"].interpolate(method="time").ffill().bfill()
    df = df.reset_index().rename(columns={"index": "datetime"})
    return df

def fetch_from_openmeteo(lat, lon, days=30):
    start = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.utcnow().strftime("%Y-%m-%d")
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "hourly": "pm2_5"
    }

    r = requests.get(url, params=params)
    data = r.json()

    if "hourly" not in data or "pm2_5" not in data["hourly"]:
        raise ValueError("No data returned from Open-Meteo.")

    df = pd.DataFrame({
        "datetime": pd.to_datetime(data["hourly"]["time"]),
        "value": data["hourly"]["pm2_5"]
    })
    return df