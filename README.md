# 🧪 DataPrep Pro Ultimate

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)]((https://sankalp-indish-dataprep-pro.streamlit.app/))
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://opensource.org/licenses/MIT)

**Transform messy, raw datasets into ML-ready assets in seconds.**

DataPrep Pro is a comprehensive data engineering tool designed to automate the painful 80% of data science: Data Cleaning and Preprocessing. It offers an intelligent pipeline that auto-detects problem types, cleans text using NLP, handles outliers, and generates professional PDF audit reports.

---

## 🚀 Key Features

* **🧠 Auto-Detection Engine:** Automatically identifies if your problem is Regression or Classification based on the target variable.
* **🧹 Smart Cleaning:** * **NLP Text Cleaning:** Removes special characters and standardizes text columns.
    * **Date Extraction:** Converts complex date objects into ML-friendly features (Year/Month/Day).
    * **Imputation:** Handles missing values with Mean/Median/Mode strategies.
* **📊 Interactive Visuals:** Built-in Exploratory Data Analysis (EDA) using Plotly (Zoom/Pan/Hover).
* **📑 Professional Reporting:** Generates a downloadable **PDF Audit Report** and **HTML Report** summarizing all actions taken.
* **🐍 Code Export:** Generates a reproducible **Python Script** (`clean_my_data.py`) corresponding to your GUI configurations.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Data Processing:** Pandas, NumPy, Scikit-Learn
* **Visualization:** Plotly Express, Seaborn, Matplotlib
* **Reporting:** FPDF (PDF Generation), Kaleido (Static Image Export)

---

## 💻 Local Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/DataPrep-Pro.git](https://github.com/yourusername/DataPrep-Pro.git)
    cd DataPrep-Pro
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## 📂 Project Structure

```text
DataPrepPro/
├── app.py                   # Main Application Entry Point
├── requirements.txt         # Project Dependencies
├── components/              # UI Components
│   ├── visuals.py           # Visualization Logic
│   └── __init__.py
└── utils/                   # Core Logic
    ├── processor.py         # Data Cleaning Pipeline
    ├── report.py            # HTML/PDF Generators
    ├── code_generator.py    # Python Script Generator
    └── __init__.py
```
---

## 👤 Author: Sankalp Indish

LinkedIn: https://www.linkedin.com/in/sankalp-indish/

Portfolio: https://sites.google.com/view/sankalp-indish/

Built with ❤️ for the Data Science Community.

---
