from .prophet_forecast import train_forecast_prophet
from .xgboost_forecast import train_xgboost
from .arima_forecast import train_arima
from .lightgbm_forecast import train_lightgbm
from .sarima_forecast import train_sarima
from .theta_forecast import train_theta
from .neuralprophet_forecast import train_neuralprophet
from .lstm_forecast import train_lstm
from .moving_average import moving_average_forecast
from .naive import naive_forecast
from .ensemble_forecast import get_ensemble_forecast

# Optional: model weight presets
BASE_WEIGHTS = {
    "prophet": 0.25,
    "xgboost": 0.2,
    "arima": 0.2,
    "lightgbm": 0.15,
    "sarima": 0.15,
    "theta": 0.1,
    "neuralprophet": 0.15,
    "lstm": 0.15,
    "moving_avg": 0.05,
    "naive": 0.05,
}