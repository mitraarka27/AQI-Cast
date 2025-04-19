import pandas as pd

from src.forecast_model.prophet_forecast import train_forecast_prophet
from src.forecast_model.xgboost_forecast import train_xgboost
from src.forecast_model.arima_forecast import train_arima
# from src.forecast_model.lightgbm_forecast import train_lightgbm
# from src.forecast_model.theta_forecast import train_theta
# from src.forecast_model.sarima_forecast import train_sarima
# from src.forecast_model.neuralprophet_forecast import train_neuralprophet
# from src.forecast_model.lstm_forecast import train_lstm

def moving_average_forecast(df, horizon=72, window=24):
    avg = df["value"].iloc[-window:].mean()
    future_times = pd.date_range(start=df["datetime"].iloc[-1], periods=horizon + 1, freq="H")[1:]
    return pd.DataFrame({"ds": future_times, "yhat": [avg] * horizon})

def naive_forecast(df, horizon=72):
    last_val = df["value"].iloc[-1]
    future_times = pd.date_range(start=df["datetime"].iloc[-1], periods=horizon + 1, freq="H")[1:]
    return pd.DataFrame({"ds": future_times, "yhat": [last_val] * horizon})

BASE_WEIGHTS = {
    "prophet": 0.25, "xgboost": 0.25, "arima": 0.15,
    "lightgbm": 0.10, "theta": 0.05, "neuralprophet": 0.05,
    "sarima": 0.10, "lstm": 0.05, "moving_avg": 0.025, "naive": 0.025
}

def get_ensemble_forecast(df, horizon=72, selected_models=None):
    if selected_models is None:
        selected_models = ["prophet", "xgboost", "arima", "moving_avg"]

    model_outputs = {}
    for model in selected_models:
        try:
            if model == "prophet": _, out = train_forecast_prophet(df, periods=horizon)
            elif model == "xgboost": _, out = train_xgboost(df, forecast_horizon=horizon)
            elif model == "arima": _, out = train_arima(df, forecast_horizon=horizon)
            # elif model == "lightgbm": _, out = train_lightgbm(df, forecast_horizon=horizon)
            # elif model == "theta": _, out = train_theta(df, forecast_horizon=horizon)
            # elif model == "sarima": _, out = train_sarima(df, forecast_horizon=horizon)
            # elif model == "neuralprophet": _, out = train_neuralprophet(df, forecast_horizon=horizon)
            # elif model == "lstm": _, out = train_lstm(df, forecast_horizon=horizon)
            elif model == "moving_avg": out = moving_average_forecast(df, horizon=horizon)
            elif model == "naive": out = naive_forecast(df, horizon=horizon)
            else: continue
            model_outputs[model] = out.rename(columns={"yhat": model})
        except Exception as e:
            import traceback
            print(f"🚫 Model `{model}` failed during forecasting:")
            traceback.print_exc()

    if not model_outputs:
        return pd.DataFrame()  # Ensure the app doesn’t crash

    # Merge all successful forecasts
    merged = None
    for name, df_out in model_outputs.items():
        if merged is None:
            merged = df_out
        else:
            merged = pd.merge(merged, df_out, on="ds", how="inner")

    model_cols = list(model_outputs.keys())
    merged["ensemble_median"] = merged[model_cols].median(axis=1)

    weights = {k: BASE_WEIGHTS.get(k, 0.05) for k in model_cols}
    total = sum(weights.values())
    weights = {k: v / total for k, v in weights.items()}

    merged["ensemble_weighted"] = sum(merged[k] * weights[k] for k in model_cols)
    return merged