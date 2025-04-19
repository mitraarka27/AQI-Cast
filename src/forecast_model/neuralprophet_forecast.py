import pandas as pd
from neuralprophet import NeuralProphet

def train_neuralprophet(df, forecast_horizon=72):
    df_n = df.rename(columns={"datetime": "ds", "value": "y"})
    model = NeuralProphet(yearly_seasonality=True, daily_seasonality=True)
    model.fit(df_n, freq="H")
    future = model.make_future_dataframe(df_n, periods=forecast_horizon)
    forecast = model.predict(future)
    return model, forecast[["ds", "yhat1"]].rename(columns={"yhat1": "yhat"})