import pandas as pd

def naive_forecast(df, horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 1:
        raise ValueError("No data available for naive forecast.")

    last = df["value"].iloc[-1]
    future_dates = pd.date_range(start=df.index[-1], periods=horizon+1, freq="h")[1:]
    forecast_df = pd.DataFrame({"ds": future_dates, "yhat": [last] * horizon})

    return forecast_df