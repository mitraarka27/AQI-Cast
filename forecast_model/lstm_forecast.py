import pandas as pd
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def train_lstm(df, forecast_horizon=72):
    df = df[["datetime", "value"]].dropna()
    df = df.set_index("datetime").asfreq("h")

    if df.empty or len(df) < 96:
        raise ValueError("Not enough data for LSTM (needs >96 hours).")

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(df[["value"]].values)

    X, y = [], []
    for i in range(24, len(scaled) - forecast_horizon):
        X.append(scaled[i-24:i, 0])
        y.append(scaled[i:i+forecast_horizon, 0])
    X, y = np.array(X), np.array(y)
    X = X.reshape((X.shape[0], X.shape[1], 1))

    model = Sequential()
    model.add(LSTM(50, input_shape=(X.shape[1], 1)))
    model.add(Dense(forecast_horizon))
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)

    last_input = scaled[-24:].reshape((1, 24, 1))
    forecast_scaled = model.predict(last_input)[0]
    forecast = scaler.inverse_transform(forecast_scaled.reshape(-1, 1)).flatten()

    future_dates = pd.date_range(start=df.index[-1], periods=forecast_horizon+1, freq="h")[1:]
    forecast_df = pd.DataFrame({"ds": future_dates, "yhat": forecast})

    return model, forecast_df