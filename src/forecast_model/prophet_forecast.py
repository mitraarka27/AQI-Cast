from prophet import Prophet
import pandas as pd

def train_forecast_prophet(df, periods=72):
    df_p = df[["datetime", "value"]].dropna()
    df_p = df_p.rename(columns={"datetime": "ds", "value": "y"})

    if df_p.empty or len(df_p) < 48:
        raise ValueError("Not enough data for Prophet.")

    model = Prophet(daily_seasonality=True)
    model.fit(df_p)

    future = model.make_future_dataframe(periods=periods, freq='h')
    forecast = model.predict(future)
    forecast_df = forecast[["ds", "yhat"]].iloc[-periods:].dropna()

    return model, forecast_df