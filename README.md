# 🌫️ Air Quality Risk Forecaster

A lightweight, interactive ML web app that forecasts air pollution risk at your location using real-time AQI data and a blend of forecasting models.

---
## 🔍 Preview

Here’s what the AQI Risk Forecaster looks like:

### 🌫️ Home UI
![Home UI](assets/landing_page.png)

### 🌫️ Interactive Map
![Interactive Map](assets/current_map.png)

### 📈 Forecast Output
![Forecast Output](assets/forecast.png)
---

## 🔍 Features

- 🛰️ **Live AQI fetch** from OpenAQ + 1-year historical PM2.5
- 🔮 **Forecasts using 10 models**: Prophet, XGBoost, LightGBM, ARIMA, LSTM, etc.
- 🗺️ **Raster-style AQI maps** (Current & Forecast)
- ⚕️ **Health risk classification** using EPA/WHO thresholds + user profile
- 🧠 **Weighted ensemble forecasts**
- 📤 **PDF report export**:
  - **Concise**: maps + trends + bullet summary
  - **Verbose**: includes model-level maps and plots
- 💾 **Zero-disk, session-only caching** to avoid bloat

---

## 🧰 Tech Stack

- Python, Streamlit
- Prophet, XGBoost, LightGBM, LSTM (Keras/Tensorflow)
- Statsmodels (ARIMA, Theta, SARIMA)
- Plotly & Matplotlib for visualization
- FPDF for export
- OpenAQ + Open-Meteo APIs for data

---

## 🚀 How to Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
