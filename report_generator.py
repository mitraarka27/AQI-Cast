from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Air Quality Risk Report", ln=True, align="C")

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.ln(5)
        self.cell(0, 10, title, ln=True)

    def image_section(self, img_path, title=None, w=180):
        if title:
            self.set_font("Arial", "B", 10)
            self.ln(2)
            self.cell(0, 10, title, ln=True)
        self.image(img_path, w=w)
        self.ln(5)

def generate_pdf_report(report_type, location, lat, lon, current_pm25, forecast_pm25, risk_info, plots, model_forecasts=None):
    pdf = PDF()
    pdf.add_page()

    # Summary
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 10, f"Location: {location} (Lat: {lat:.2f}, Lon: {lon:.2f})", ln=True)
    pdf.cell(0, 10, f"Current PM2.5: {current_pm25:.1f} µg/m³", ln=True)
    pdf.cell(0, 10, f"Forecast PM2.5: {forecast_pm25:.1f} µg/m³", ln=True)
    pdf.cell(0, 10, f"Base Risk: {risk_info['base_risk']}", ln=True)
    pdf.cell(0, 10, f"Adjusted Risk: {risk_info['adjusted_risk']}", ln=True)

    # Images
    pdf.section_title("Current AQ Map")
    pdf.image_section(plots["current_map"])

    pdf.section_title("Forecast AQ Map")
    pdf.image_section(plots["forecast_map"])

    pdf.section_title("Forecast Time Series")
    pdf.image_section(plots["forecast_timeseries"])

    # Optional model forecasts
    if report_type == "verbose" and model_forecasts:
        pdf.section_title("Individual Model Forecasts")
        for model_name, path in model_forecasts.items():
            pdf.image_section(path, title=model_name)

    output_path = os.path.join(os.path.expanduser("~"), "Desktop", f"AQI_Report_{lat:.2f}_{lon:.2f}.pdf")
    pdf.output(output_path)
    return output_path