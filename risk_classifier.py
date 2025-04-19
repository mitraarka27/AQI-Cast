AQI_THRESHOLDS = [
    (0.0, 12.0, "Good"),
    (12.1, 35.4, "Moderate"),
    (35.5, 55.4, "Unhealthy for Sensitive Groups"),
    (55.5, 150.4, "Unhealthy"),
    (150.5, 250.4, "Very Unhealthy"),
    (250.5, float("inf"), "Hazardous"),
]

SENSITIVITY_OFFSET = {
    "General": 0,
    "Outdoor Worker": 1,
    "Child": 1,
    "Elderly": 1,
    "Asthmatic": 2
}

def classify_aqi(pm25_value, profile="General"):
    base_index = None
    for i, (low, high, label) in enumerate(AQI_THRESHOLDS):
        if low <= pm25_value <= high:
            base_index = i
            break

    if base_index is None:
        return {"error": "Invalid PM2.5 value"}

    offset = SENSITIVITY_OFFSET.get(profile, 0)
    adjusted_index = min(base_index + offset, len(AQI_THRESHOLDS) - 1)

    return {
        "pm25_value": pm25_value,
        "profile": profile,
        "base_risk": AQI_THRESHOLDS[base_index][2],
        "adjusted_risk": AQI_THRESHOLDS[adjusted_index][2],
        "risk_shift": offset
    }