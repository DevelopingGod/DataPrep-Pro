import base64
import io
import os
import tempfile
from fpdf import FPDF
import plotly.io as pio # NEW IMPORT

# ==========================
# 1. HTML REPORT GENERATOR
# ==========================
def generate_html_report(df_raw, df_clean, logs, figures):
    """
    Generates a professionally styled HTML report with INTERACTIVE Plotly charts.
    """
    # Stats
    rows_dropped = len(df_raw) - len(df_clean)
    missing_fixed = df_raw.isnull().sum().sum() - df_clean.isnull().sum().sum()
    
    # --- 1. Correlation Heatmap (Static Image) ---
    corr_html = "<p><em>No correlation plot generated.</em></p>"
    if 'correlation' in figures:
        buf = io.BytesIO()
        figures['correlation'].savefig(buf, format="png", bbox_inches='tight')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode("utf-8")
        corr_html = f'<div class="chart-container"><img src="data:image/png;base64,{img_str}" style="max-width:100%;"></div>'

    # --- 2. Interactive Chart (Plotly HTML) ---
    # We convert the figure to a DIV string containing the JS script.
    interactive_html = "<p><em>No interactive chart selected.</em></p>"
    if 'interactive' in figures:
        # include_plotlyjs='cdn' keeps the file size small (fetches JS from internet)
        interactive_html = pio.to_html(figures['interactive'], full_html=False, include_plotlyjs='cdn')

    # Logs
    log_html = "<ul>" + "".join([f"<li>{log}</li>" for log in logs]) + "</ul>"

    # HTML Template
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>DataPrep Analysis Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; padding: 20px; background-color: #f4f4f9; }}
            .container {{ max-width: 1000px; margin: auto; background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2C3E50; border-bottom: 3px solid #3498DB; padding-bottom: 10px; }}
            h2 {{ color: #2C3E50; margin-top: 40px; border-left: 5px solid #3498DB; padding-left: 10px; }}
            .metric-box {{ display: flex; gap: 20px; margin-bottom: 20px; }}
            .metric {{ flex: 1; background: #EAF2F8; padding: 15px; border-radius: 5px; text-align: center; }}
            .metric strong {{ display: block; font-size: 1.5em; color: #3498DB; }}
            .chart-container {{ text-align: center; margin: 20px 0; border: 1px solid #eee; padding: 10px; border-radius: 5px; }}
            li {{ margin-bottom: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧪 DataPrep Pro Analysis Report</h1>
            <p>Generated automatically by the Universal Data Processing Engine.</p>
            
            <h2>📊 Executive Summary</h2>
            <div class="metric-box">
                <div class="metric"><strong>{len(df_raw)}</strong>Original Rows</div>
                <div class="metric"><strong>{len(df_clean)}</strong>Processed Rows</div>
                <div class="metric"><strong>{missing_fixed}</strong>Missing Fixed</div>
            </div>

            <h2>🛠️ Processing Logs</h2>
            {log_html}

            <h2>🔥 Correlation Matrix</h2>
            <p>Static heatmap of numerical feature correlations:</p>
            {corr_html}

            <h2>📊 User Insights</h2>
            <p>Interactive visualization selected during analysis:</p>
            <div class="chart-container">
                {interactive_html}
            </div>
        </div>
    </body>
    </html>
    """
    return html

# ==========================
# 2. PDF REPORT GENERATOR
# ==========================
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'DataPrep Pro - Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(df_raw, df_clean, logs, figures):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Executive Summary
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Executive Summary", 0, 1)
    pdf.set_font("Arial", size=11)
    
    pdf.cell(0, 8, f"Original Dataset: {df_raw.shape[0]} rows, {df_raw.shape[1]} columns", 0, 1)
    pdf.cell(0, 8, f"Processed Dataset: {df_clean.shape[0]} rows, {df_clean.shape[1]} columns", 0, 1)
    missing_fixed = df_raw.isnull().sum().sum() - df_clean.isnull().sum().sum()
    pdf.cell(0, 8, f"Total Missing Values Fixed: {missing_fixed}", 0, 1)
    pdf.ln(5)

    # Logs
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Processing Actions Taken", 0, 1)
    pdf.set_font("Arial", size=10)
    for log in logs:
        clean_log = log.encode('latin-1', 'replace').decode('latin-1') 
        pdf.multi_cell(0, 6, f"- {clean_log}")
    pdf.ln(5)

    # Visualizations
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Key Visualizations", 0, 1)
    
    def embed_image(fig, title, is_plotly=False):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                if is_plotly:
                    fig.write_image(tmp.name, width=800, height=500, scale=2)
                else:
                    fig.savefig(tmp.name, format="png", bbox_inches='tight', dpi=100)
                
                pdf.ln(5)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, title, 0, 1)
                pdf.image(tmp.name, x=10, w=190)
                pdf.ln(5)
            os.unlink(tmp.name)
        except Exception as e:
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 10, f"(Could not render chart: {str(e)})", 0, 1)

    if 'correlation' in figures:
        embed_image(figures['correlation'], "Correlation Matrix", is_plotly=False)
    
    if 'interactive' in figures:
        if pdf.get_y() > 200: pdf.add_page()
        embed_image(figures['interactive'], "User Selected Chart", is_plotly=True)

    return pdf.output(dest='S').encode('latin-1')