import pandas as pd
from statsmodels.tsa.forecasting.theta import ThetaModel

def train_theta(df, forecast_horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 48:
        raise ValueError("Not enough data for Theta Model.")

    model = ThetaModel(df["value"], period=24)
    model_fit = model.fit()
    forecast = model_fit.forecast(forecast_horizon)

    future_dates = pd.date_range(start=df.index[-1], periods=forecast_horizon+1, freq="h")[1:]
    forecast_df = pd.DataFrame({"ds": future_dates, "yhat": forecast.values})

    return model_fit, forecast_df