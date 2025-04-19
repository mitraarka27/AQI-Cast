import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor

def train_lightgbm(df, forecast_horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 48:
        raise ValueError("Not enough data for LightGBM.")

    df["hour"] = df.index.hour
    df["dayofweek"] = df.index.dayofweek
    df["lag1"] = df["value"].shift(1)
    df = df.dropna()

    X = df[["hour", "dayofweek", "lag1"]]
    y = df["value"]

    model = LGBMRegressor()
    model.fit(X, y)

    future_dates = pd.date_range(start=df.index[-1], periods=forecast_horizon+1, freq="h")[1:]
    preds = []
    last_value = df["value"].iloc[-1]

    for date in future_dates:
        features = pd.DataFrame({
            "hour": [date.hour],
            "dayofweek": [date.dayofweek],
            "lag1": [last_value]
        })
        yhat = model.predict(features)[0]
        preds.append((date, yhat))
        last_value = yhat

    forecast_df = pd.DataFrame(preds, columns=["ds", "yhat"])
    return model, forecast_df