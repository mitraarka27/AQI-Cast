import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

def train_sarima(df, forecast_horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 48:
        raise ValueError("Not enough data for SARIMA.")

    model = SARIMAX(df["value"], order=(1, 1, 1), seasonal_order=(1, 0, 1, 24))
    model_fit = model.fit(disp=False)

    forecast = model_fit.forecast(steps=forecast_horizon)
    future_dates = pd.date_range(start=df.index[-1], periods=forecast_horizon+1, freq="h")[1:]
    forecast_df = pd.DataFrame({"ds": future_dates, "yhat": forecast})

    return model_fit, forecast_df