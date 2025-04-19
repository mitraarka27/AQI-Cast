import pandas as pd

def moving_average_forecast(df, horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 48:
        raise ValueError("Not enough data for Moving Average.")

    avg = df["value"].tail(24).mean()
    future_dates = pd.date_range(start=df.index[-1], periods=horizon+1, freq="h")[1:]
    forecast_df = pd.DataFrame({"ds": future_dates, "yhat": [avg] * horizon})

    return forecast_df