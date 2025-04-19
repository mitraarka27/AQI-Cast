import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def train_arima(df, forecast_horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 48:
        raise ValueError("Not enough data for ARIMA.")

    model = ARIMA(df["value"], order=(1, 1, 1))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=forecast_horizon)
    future_dates = pd.date_range(start=df.index[-1], periods=forecast_horizon+1, freq="h")[1:]
    forecast_df = pd.DataFrame({"ds": future_dates, "yhat": forecast})

    return model_fit, forecast_df