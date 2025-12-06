import streamlit as st
import pandas as pd
import time

# --- IMPORT MODULES ---
from utils.processor import AdvancedProcessor
from utils.report import generate_html_report, generate_pdf_report
from utils.code_generator import generate_python_code
from components.visuals import render_visuals_tab

# Page Config
st.set_page_config(
    page_title="DataPrep Pro Ultimate", 
    page_icon="🧪", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS (RESPONSIVE) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* TABS STYLING - Responsive */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        padding: 10px 0px;
        flex-wrap: wrap; /* Key for mobile: Allows tabs to wrap */
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        min-height: 50px;
        white-space: normal; /* Key for mobile: Allows text to wrap inside tab */
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        gap: 5px;
        padding: 10px 20px;
        font-weight: 600;
        color: #555;
        border: 1px solid #eee;
        transition: all 0.3s ease;
        flex-grow: 1; /* Key for mobile: Tabs expand to fill row */
        justify-content: center;
        text-align: center;
    }

    .stTabs [aria-selected="true"] {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #4CAF50;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }

    /* Mobile Media Query for Text Sizes */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] { font-size: 0.85rem; padding: 8px; }
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.2rem !important; }
        .stMarkdown p { font-size: 0.9rem; }
    }

    /* METRIC CARDS */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }

    /* FOOTER */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #888;
        text-align: center;
        padding: 10px;
        border-top: 1px solid #eee;
        font-size: 12px;
        z-index: 9999;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None
if "logs" not in st.session_state:
    st.session_state.logs = []

# --- SIDEBAR: NAVIGATION & INFO ---
with st.sidebar:    
    st.title("🧪 DataPrep Pro")
    st.caption("The Ultimate Data Cleaning Engine")
    st.markdown("---")
    
    st.header("📂 Data Source")
    uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "xlsx"])
    
    # Initialize variables
    target_col = None
    df_raw = None 
    problem_type = "Regression"
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_raw = pd.read_csv(uploaded_file)
            else:
                df_raw = pd.read_excel(uploaded_file)
            
            st.success("✅ File Uploaded!")
            
            st.subheader("🎯 Target Variable")
            target_col = st.selectbox("Select Output Column", ["None"] + list(df_raw.columns))
            if target_col == "None": target_col = None
            
            st.subheader("🧠 Problem Type")
            default_prob = "Regression"
            if target_col and df_raw[target_col].nunique() < 20:
                default_prob = "Classification"
            
            options = ["Regression", "Classification", "Clustering"]
            problem_type = st.selectbox("Analysis Type", options, index=options.index(default_prob))
            st.info(f"Auto-detected: **{default_prob}**")

        except Exception as e:
            st.error(f"Error: {e}")
            df_raw = None

    # Reset state on new upload
    if st.session_state.processed_data is not None and uploaded_file is None:
        st.session_state.processed_data = None
        st.session_state.logs = []

    # --- ABOUT THE DEVELOPER ---
    st.markdown("---")
    st.markdown("### 👨‍💻 About")
    st.markdown("""**Sankalp Indish**""")
    st.markdown("""*Data Scientist | AI Researcher*""")
    
    # Social Buttons (Responsive Flexbox)
    st.markdown("""
    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
        <a href="https://linkedin.com/in/sankalp-indish" target="_blank" style="text-decoration: none; flex-grow: 1;">
            <button style="width: 100%; background-color: #0077b5; color: white; border: none; padding: 8px; border-radius: 5px; cursor: pointer;">LinkedIn</button>
        </a>
        <a href="https://sites.google.com/view/sankalp-indish" target="_blank" style="text-decoration: none; flex-grow: 1;">
            <button style="width: 100%; background-color: #333; color: white; border: none; padding: 8px; border-radius: 5px; cursor: pointer;">Portfolio</button>
        </a>
    </div>
    """, unsafe_allow_html=True)


# --- MAIN APPLICATION LOGIC ---
st.title("🧪 DataPrep Pro Ultimate")
st.markdown("#### Transform messy data into ML-ready assets.")

if uploaded_file and df_raw is not None:
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Overview", "📈 Visual Insights", "🛠️ Configuration", "📥 Results"])

    # === TAB 1: OVERVIEW ===
    with tab1:
        # Use container width ensures metrics stretch on mobile
        c1, c2, c3 = st.columns(3)
        c1.metric("Rows", df_raw.shape[0])
        c2.metric("Columns", df_raw.shape[1])
        c3.metric("Duplicates", df_raw.duplicated().sum(), delta_color="inverse")
        
        st.subheader("Dataset Preview")
        st.dataframe(df_raw.head(), use_container_width=True)
        
        st.subheader("Column Analysis")
        info_df = pd.DataFrame({
            'Type': df_raw.dtypes.astype(str),
            'Missing': df_raw.isnull().sum(),
            'Missing %': (df_raw.isnull().sum() / len(df_raw)) * 100
        })
        st.dataframe(info_df, use_container_width=True)

    # === TAB 2: VISUALS ===
    with tab2:
        visual_figures = render_visuals_tab(df_raw)

    # === TAB 3: CONFIGURATION ===
    with tab3:
        st.header("⚙️ Configure Pipeline")
        default_balance = True if problem_type == "Classification" else False
        default_outlier = True if problem_type == "Regression" else False
        
        col_L, col_R = st.columns(2)
        with col_L:
            st.subheader("1. Feature Engineering")
            enable_datetime = st.checkbox("Extract Date Features", value=True)
            # NLP Option
            enable_text = st.checkbox("Clean Text Data (NLP)", value=False, help="Lowercases & removes punctuation from text columns.")
            
            st.divider()
            st.subheader("2. Missing Values")
            enable_missing = st.checkbox("Handle Missing", value=True)
            missing_strategy = st.selectbox("Imputation", ["mean", "median", "mode", "drop"], disabled=not enable_missing)
            
            st.divider()
            st.subheader("3. Outliers")
            enable_outliers = st.checkbox("Handle Outliers", value=default_outlier)
            outlier_method = st.selectbox("Method", ["iqr", "z-score"], disabled=not enable_outliers)
            outlier_action = st.radio("Action", ["cap", "trim"], disabled=not enable_outliers)

        with col_R:
            st.subheader("4. Encoding")
            enable_encoding = st.checkbox("Encode Categories", value=True)
            encoding_method = st.radio("Encoding", ["label", "one-hot"], disabled=not enable_encoding)
            
            st.divider()
            st.subheader("5. Scaling & Balancing")
            enable_scaling = st.checkbox("Scale Features", value=False)
            scaling_method = st.selectbox("Scaler", ["standard", "minmax"], disabled=not enable_scaling)
            enable_balance = st.checkbox("Balance Target Class", value=default_balance, disabled=not target_col)

        config = {
            'target_col': target_col,
            'datetime': {'enable': enable_datetime},
            'text_clean': {'enable': enable_text}, # NLP Config passed here
            'missing_values': {'enable': enable_missing, 'strategy': missing_strategy},
            'outliers': {'enable': enable_outliers, 'method': outlier_method, 'treatment': outlier_action},
            'encoding': {'enable': enable_encoding, 'method': encoding_method},
            'scaling': {'enable': enable_scaling, 'method': scaling_method},
            'balancing': {'enable': enable_balance}
        }

    # === TAB 4: PROCESS & RESULTS ===
    with tab4:
        st.header("🚀 Run Pipeline")
        
        # Primary Button with Full Width for Mobile
        if st.button("Start Processing", type="primary", use_container_width=True):
            with st.spinner("Analyzing and cleaning data..."):
                processor = AdvancedProcessor(df_raw, config)
                clean_df, logs = processor.process()
                st.session_state.processed_data = clean_df
                st.session_state.logs = logs
                time.sleep(1)
            st.success("✅ Processing Complete!")

        if st.session_state.processed_data is not None:
            clean_df = st.session_state.processed_data
            logs = st.session_state.logs
            
            with st.expander("📝 View Logs"):
                for log in logs: st.write(f"- {log}")
            
            st.subheader("Results")
            c1, c2 = st.columns(2)
            c1.info(f"Original: {df_raw.shape}")
            c2.success(f"Processed: {clean_df.shape}")
            st.dataframe(clean_df.head(), use_container_width=True)
            
            st.divider()
            st.subheader("📥 Export Results")
            
            # Responsive Grid: 2 columns on all devices (stacks cleanly)
            r1c1, r1c2 = st.columns(2)
            r2c1, r2c2 = st.columns(2)
            
            csv = clean_df.to_csv(index=False).encode('utf-8')
            r1c1.download_button("💾 CSV Data", csv, "clean_data.csv", "text/csv", use_container_width=True)
            
            try:
                html_rep = generate_html_report(df_raw, clean_df, logs, visual_figures)
                r1c2.download_button("🌐 HTML Report", html_rep, "report.html", "text/html", use_container_width=True)
            except: r1c2.error("HTML Error")

            try:
                pdf_rep = generate_pdf_report(df_raw, clean_df, logs, visual_figures)
                r2c1.download_button("📄 PDF Report", pdf_rep, "report.pdf", "application/pdf", use_container_width=True)
            except: r2c1.error("PDF Error")

            py_code = generate_python_code(config, uploaded_file.name)
            r2c2.download_button("🐍 Python Code", py_code, "script.py", "text/x-python", use_container_width=True)

else:
    st.info("👈 Please upload a dataset to begin.")
    st.markdown("### Features:\n- **Auto-Detection:** ML Task ID.\n- **Smart Cleaning:** Imputation & Outliers.\n- **Visuals:** Interactive Plotly Charts.\n- **NLP:** Text Cleaning.")

# --- FOOTER ---
st.markdown("""
<div class="footer">
    <p>Developed with ❤️ by <b>Sankalp Indish</b> | © 2025 DataPrep Pro</p>
</div>
""", unsafe_allow_html=True)