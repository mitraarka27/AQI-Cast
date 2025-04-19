# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import tempfile
import os

from src.utils import get_coords_from_city
from src.historical_fetcher import fetch_from_openaq_v3, fetch_from_openmeteo
from src.risk_classifier import classify_aqi
from src.forecast_model.ensemble_forecast import get_ensemble_forecast
from src.raster_map_handler import fetch_raster_pm25, fake_raster_from_point, scale_forecast_raster
from src.report_generator import generate_pdf_report

st.set_page_config(page_title="Air Quality Risk Forecaster", layout="centered")
st.title("🌫️ Air Quality Risk Forecaster")
st.markdown(
    """
    <div style='text-align: center; font-size: 18px; padding: 6px 0 12px 0;'>
        <strong>Developed by <a href='https://github.com/mitraarka27' target='_blank'>Arka Mitra</a></strong> 🛠️
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("Forecast PM2.5 and assess health risks using real-time data and machine learning.")

# Location input
input_mode = st.radio("📍 Choose input mode", ["City", "Coordinates"], horizontal=True)

if input_mode == "City":
    city = st.text_input("Enter city name", value="New Delhi")
    lat, lon = get_coords_from_city(city)
else:
    lat = st.number_input("Latitude", value=28.61, format="%.4f")
    lon = st.number_input("Longitude", value=77.23, format="%.4f")

st.success(f"Using location: ({lat:.2f}, {lon:.2f})")

# User options
profile = st.selectbox("👤 Health Profile", ["General", "Child", "Elderly", "Asthmatic", "Outdoor Worker"])
selected_models = st.multiselect("🧠 Forecast Models", [
    "prophet", "xgboost", "arima", "lightgbm", "theta", "sarima", "neuralprophet", "lstm", "moving_avg", "naive"
], default=["prophet", "xgboost", "arima"])
horizon = st.slider("⏱️ Forecast Horizon (Hours)", 24, 168, 72, step=24)

# Fetch historical data
try:
    df_hist = fetch_from_openaq_v3(lat, lon, days=30)
    data_source = "OpenAQ (nearest station)"
except ValueError:
    df_hist = fetch_from_openmeteo(lat, lon, days=30)
    data_source = "Open-Meteo (global model)"

st.session_state.df_hist = df_hist
st.success(f"📡 Data source used: **{data_source}**")

# Forecasting
with st.spinner("Generating forecast..."):
    df_forecast = get_ensemble_forecast(df_hist, horizon=horizon, selected_models=selected_models)

if df_forecast.empty or "ensemble_weighted" not in df_forecast.columns:
    st.error("❌ Forecasting failed. Try selecting different models or location.")
    st.stop()

# Compute scale factor
current_pm = df_hist["value"].iloc[-1]
future_pm = df_forecast["ensemble_weighted"].iloc[-1]
scale_factor = future_pm / current_pm if current_pm > 0 else 1.0

st.session_state.current_pm = current_pm
st.session_state.future_pm = future_pm
st.session_state.scale_factor = scale_factor

# Risk classification
risk_info = classify_aqi(current_pm, profile)

# Raster maps — fallback guaranteed
try:
    latest_pm25 = fetch_raster_pm25(lat, lon)
    if pd.isna(latest_pm25):
        raise ValueError("Raster fetch returned NaN")
except:
    latest_pm25 = current_pm

st.session_state.df_current_map = fake_raster_from_point(lat, lon, latest_pm25)
df_current_map = st.session_state.df_current_map
df_forecast_map = scale_forecast_raster(df_current_map, scale_factor)

# Map plot (continuous grid via density map)
st.subheader("🗺️ AQI Map")
view = st.radio("Map View", ["Current", "Forecast"], horizontal=True)
df_map = df_current_map if view == "Current" else df_forecast_map
map_title = f"{view} PM2.5 (µg/m³)"

fig = px.density_mapbox(
    df_map,
    lat="latitude",
    lon="longitude",
    z="value",
    radius=20,
    center={"lat": lat, "lon": lon},
    zoom=8,
    height=500,
    color_continuous_scale="turbo",
    range_color=[0,200],
    opacity=0.4,  
    title=map_title
)
fig.update_layout(
    mapbox_style="open-street-map",
    coloraxis_colorbar=dict(
        orientation="h",
        title="PM2.5 (µg/m³)",
        x=0.5,
        xanchor="center",
        y=-0.25
    ),
    margin={"r":0,"t":30,"l":0,"b":0}
)
fig.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":30,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=False)

# Time series plot
st.subheader("📈 Local Forecast")
fig2, ax = plt.subplots(figsize=(10, 4))
ax.plot(df_hist["datetime"], df_hist["value"], label="Observed", alpha=0.5)
ax.plot(df_forecast["ds"], df_forecast["ensemble_weighted"], label="Forecast", color="black", linewidth=2)
ax.set_ylabel("PM2.5 (µg/m³)")
ax.set_title(f"Forecast for ({lat:.2f}, {lon:.2f})")
ax.legend()
ax.tick_params(axis='x', rotation=30)
fig2.autofmt_xdate()
st.pyplot(fig2)

# Risk summary
st.subheader("🚨 Health Risk Classification")
st.markdown(f"**Current PM2.5:** {current_pm:.1f} µg/m³")
st.markdown(f"**Base Risk Level:** {risk_info['base_risk']}")
st.markdown(f"**Adjusted Risk (for {profile}):** {risk_info['adjusted_risk']}")

# Save plot (dual support)
def save_plot(fig_obj, name):
    path = os.path.join(tempfile.gettempdir(), f"{name}.png")
    if hasattr(fig_obj, "write_image"):  # Plotly
        fig_obj.write_image(path, format="png")
    elif hasattr(fig_obj, "savefig"):  # Matplotlib
        fig_obj.savefig(path, bbox_inches="tight")
    else:
        raise ValueError(f"Unsupported figure type: {type(fig_obj)}")
    return path

# Export report
st.subheader("📤 Export Report")
report_type = st.radio("Choose Report Type", ["Concise", "Verbose"], horizontal=True)

if st.button("📝 Download PDF Report"):
    with st.spinner("Generating report..."):
        current_map_path = save_plot(fig, "current_map")
        forecast_map_path = save_plot(fig, "forecast_map")
        fig2_path = save_plot(fig2, "forecast_timeseries")

        model_plots = {}
        if report_type.lower() == "verbose":
            for model in selected_models:
                if model in df_forecast.columns:
                    fig_model, ax_model = plt.subplots(figsize=(8, 3))
                    ax_model.plot(df_forecast["ds"], df_forecast[model], label=model)
                    ax_model.set_title(f"{model} Forecast")
                    ax_model.set_ylabel("PM2.5")
                    ax_model.legend()
                    ax_model.tick_params(axis='x', rotation=30)
                    fig_model.autofmt_xdate()
                    model_path = save_plot(fig_model, f"{model}_forecast")
                    model_plots[model] = model_path

        pdf_path = generate_pdf_report(
            report_type=report_type.lower(),
            location=f"{lat:.2f}, {lon:.2f}",
            lat=lat,
            lon=lon,
            current_pm25=current_pm,
            forecast_pm25=future_pm,
            risk_info=risk_info,
            plots={
                "current_map": current_map_path,
                "forecast_map": forecast_map_path,
                "forecast_timeseries": fig2_path
            },
            model_forecasts=model_plots if report_type.lower() == "verbose" else None
        )

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📄 Click to Download Your Report",
                data=f,
                file_name=os.path.basename(pdf_path),
                mime="application/pdf"
            )

if st.button("🔄 Reset Session"):
    st.session_state.clear()
    st.experimental_rerun()