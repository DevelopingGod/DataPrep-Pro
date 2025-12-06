import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd
import io
import numpy as np

def render_visuals_tab(df):
    """
    Renders charts and returns a dictionary of figures 
    to be used in the PDF report.
    """
    figures = {} # Store figures here
    
    st.header("📈 Exploratory Data Analysis")
    
    # --- 1. Correlation Heatmap (Seaborn) ---
    with st.expander("🔥 Correlation Heatmap", expanded=True):
        num_df = df.select_dtypes(include=['float64', 'int64'])
        if not num_df.empty and st.checkbox("Show Heatmap", value=True):
            fig_corr, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(num_df.corr(), annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
            st.pyplot(fig_corr)
            figures['correlation'] = fig_corr # Store for report

    st.divider()

    # --- 2. Interactive Chart Builder (Plotly) ---
    st.subheader("📊 Interactive Chart Builder")
    chart_type = st.selectbox(
        "Choose Chart Type", 
        ["Histogram", "Box Plot", "Scatter Plot", "Pie Chart"]
    )

    fig = None
    
    if chart_type == "Histogram":
        col1, col2 = st.columns(2)
        x_col = col1.selectbox("Select Column", df.columns)
        color_col = col2.selectbox("Color By", ["None"] + list(df.columns))
        color = None if color_col == "None" else color_col
        fig = px.histogram(df, x=x_col, color=color, barmode="overlay", title=f"Distribution of {x_col}")

    elif chart_type == "Box Plot":
        col1, col2 = st.columns(2)
        y_col = col1.selectbox("Y-Axis (Numerical)", df.select_dtypes(include=np.number).columns)
        x_col = col2.selectbox("X-Axis (Group By)", ["None"] + list(df.columns))
        x = None if x_col == "None" else x_col
        fig = px.box(df, y=y_col, x=x, color=x, title=f"Box Plot of {y_col}")

    elif chart_type == "Scatter Plot":
        num_cols = df.select_dtypes(include=np.number).columns
        if len(num_cols) >= 2:
            col1, col2, col3 = st.columns(3)
            x = col1.selectbox("X-Axis", num_cols, index=0)
            y = col2.selectbox("Y-Axis", num_cols, index=1)
            c = col3.selectbox("Color", ["None"] + list(df.columns))
            color = None if c == "None" else c
            fig = px.scatter(df, x=x, y=y, color=color, title=f"{x} vs {y}")

    elif chart_type == "Pie Chart":
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols) > 0:
            target = st.selectbox("Category", cat_cols)
            # Limit to top 10 to avoid messy charts
            top_10 = df[target].value_counts().head(10).index
            df_filtered = df[df[target].isin(top_10)]
            fig = px.pie(df_filtered, names=target, title=f"Top 10: {target}")

    if fig:
        st.plotly_chart(fig, use_container_width=True)
        figures['interactive'] = fig # Store for report

    return figures